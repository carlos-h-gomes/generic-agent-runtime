#!/usr/bin/env python3
"""Run one command with timeout, descendant cleanup, minimized stdin, and bounded output."""

from __future__ import annotations

import argparse
from collections import deque
import ctypes
from ctypes import wintypes
import os
import signal
import subprocess
import sys
import threading
import time


class WindowsJob:
    """Kill-on-close Job Object; unavailable on non-Windows or assignment failure."""

    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    JobObjectExtendedLimitInformation = 9

    def __init__(self) -> None:
        self.handle = None
        if os.name != "nt":
            return

        class IO_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("ReadOperationCount", ctypes.c_uint64),
                ("WriteOperationCount", ctypes.c_uint64),
                ("OtherOperationCount", ctypes.c_uint64),
                ("ReadTransferCount", ctypes.c_uint64),
                ("WriteTransferCount", ctypes.c_uint64),
                ("OtherTransferCount", ctypes.c_uint64),
            ]

        class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", ctypes.c_int64),
                ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD),
            ]

        class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
                ("IoInfo", IO_COUNTERS),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t),
            ]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        kernel32.SetInformationJobObject.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
        ]
        handle = kernel32.CreateJobObjectW(None, None)
        if not handle:
            return
        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = self.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not kernel32.SetInformationJobObject(
            handle,
            self.JobObjectExtendedLimitInformation,
            ctypes.byref(info),
            ctypes.sizeof(info),
        ):
            kernel32.CloseHandle(handle)
            return
        self.handle = handle
        self.kernel32 = kernel32

    def assign(self, process: subprocess.Popen[bytes]) -> bool:
        if self.handle is None:
            return False
        process_handle = wintypes.HANDLE(int(process._handle))  # type: ignore[attr-defined]
        if not self.kernel32.AssignProcessToJobObject(self.handle, process_handle):
            self.close()
            return False
        return True

    def terminate(self, exit_code: int = 1) -> bool:
        return bool(
            self.handle is not None
            and self.kernel32.TerminateJobObject(self.handle, wintypes.UINT(exit_code))
        )

    def close(self) -> None:
        if self.handle is not None:
            self.kernel32.CloseHandle(self.handle)
            self.handle = None


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--label", default="command")
    result.add_argument("--timeout", type=float, default=300)
    result.add_argument("--grace", type=float, default=5)
    result.add_argument("--tail-lines", type=int, default=120)
    result.add_argument("--max-buffer-bytes", type=int, default=262144)
    result.add_argument("command", nargs=argparse.REMAINDER)
    return result


def windows_taskkill(pid: int, timeout: float) -> None:
    try:
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            timeout=max(1.0, timeout),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass


def terminate_tree(process: subprocess.Popen[bytes], grace: float, job: WindowsJob) -> None:
    if os.name == "nt":
        if not job.terminate():
            windows_taskkill(process.pid, grace)
            if process.poll() is None:
                try:
                    process.kill()
                except OSError:
                    pass
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except (ProcessLookupError, OSError):
            pass
    try:
        process.wait(timeout=max(0.1, grace))
        return
    except subprocess.TimeoutExpired:
        pass
    if os.name == "nt":
        if not job.terminate():
            windows_taskkill(process.pid, grace)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, OSError):
            pass


def cleanup_descendants(process: subprocess.Popen[bytes], grace: float, job: WindowsJob) -> None:
    if os.name == "nt":
        job.close()
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except (ProcessLookupError, OSError):
        return
    deadline = time.monotonic() + max(0.1, grace)
    while time.monotonic() < deadline:
        try:
            os.killpg(process.pid, 0)
        except (ProcessLookupError, OSError):
            return
        time.sleep(0.05)
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, OSError):
        pass


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        print("FAIL no command supplied", file=sys.stderr)
        return 2
    if args.timeout <= 0 or args.grace <= 0 or args.tail_lines < 1 or args.max_buffer_bytes < 4096:
        print("FAIL invalid execution limits", file=sys.stderr)
        return 2

    print(f"==> {args.label} (timeout {args.timeout:g}s)", flush=True)
    chunks: deque[bytes] = deque()
    buffered = 0
    lock = threading.Lock()
    verbose = os.environ.get("HARNESS_VERBOSE") == "1"
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    job = WindowsJob()
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=os.name != "nt",
            creationflags=flags,
        )
    except OSError as exc:
        job.close()
        print(f"FAIL {args.label}: {exc}", file=sys.stderr)
        return 127
    if os.name == "nt" and not job.assign(process):
        windows_taskkill(process.pid, args.grace)
        try:
            process.wait(timeout=max(0.1, args.grace))
        except subprocess.TimeoutExpired:
            process.kill()
        print(
            f"FAIL {args.label}: Windows Job Object containment unavailable; command stopped",
            file=sys.stderr,
        )
        return 2
    if os.name != "nt":
        job.assign(process)

    def reader() -> None:
        nonlocal buffered
        assert process.stdout is not None
        while True:
            block = process.stdout.read(8192)
            if not block:
                break
            if verbose:
                sys.stdout.buffer.write(block)
                sys.stdout.buffer.flush()
            with lock:
                chunks.append(block)
                buffered += len(block)
                while chunks and buffered > args.max_buffer_bytes:
                    buffered -= len(chunks.popleft())

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    started = time.monotonic()
    timed_out = False
    heartbeat = started + 30
    while process.poll() is None:
        elapsed = time.monotonic() - started
        if elapsed >= args.timeout:
            timed_out = True
            terminate_tree(process, args.grace, job)
            break
        if time.monotonic() >= heartbeat:
            print(f"RUNNING {args.label} ({elapsed:.0f}s)", flush=True)
            heartbeat += 30
        time.sleep(min(0.2, max(0.01, args.timeout - elapsed)))

    try:
        process.wait(timeout=max(0.1, args.grace))
    except subprocess.TimeoutExpired:
        terminate_tree(process, args.grace, job)
    cleanup_descendants(process, args.grace, job)
    thread.join(timeout=max(1, args.grace))
    elapsed = time.monotonic() - started
    with lock:
        text = b"".join(chunks).decode("utf-8", errors="replace")
        lines = text.splitlines()
    if len(lines) > args.tail_lines:
        lines = [
            f"... output truncated; showing last {args.tail_lines} lines ...",
            *lines[-args.tail_lines :],
        ]
    tail = "\n".join(lines)
    if timed_out:
        if tail and not verbose:
            print(tail, file=sys.stderr)
        print(f"TIMEOUT {args.label} after {elapsed:.1f}s", file=sys.stderr)
        return 124
    code = process.returncode if process.returncode is not None else 125
    if code == 0:
        print(f"PASS {args.label} ({elapsed:.1f}s)")
        return 0
    if tail and not verbose:
        print(tail, file=sys.stderr)
    print(f"FAIL {args.label} (exit {code}, {elapsed:.1f}s)", file=sys.stderr)
    return code if 0 < code < 126 else 1


if __name__ == "__main__":
    raise SystemExit(main())
