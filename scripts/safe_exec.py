#!/usr/bin/env python3
"""Run one command with a timeout, process-group cleanup, and bounded output."""
from __future__ import annotations
import argparse
from collections import deque
import os, signal, subprocess, sys, threading, time

def parser():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--label',default='command'); p.add_argument('--timeout',type=float,default=300); p.add_argument('--grace',type=float,default=5); p.add_argument('--tail-lines',type=int,default=120); p.add_argument('--max-buffer-bytes',type=int,default=262144); p.add_argument('command',nargs=argparse.REMAINDER); return p

def terminate_tree(process, grace):
    if process.poll() is not None: return
    try:
        if os.name=='nt': process.terminate()
        else: os.killpg(process.pid, signal.SIGTERM)
    except (ProcessLookupError,OSError): pass
    try: process.wait(timeout=max(.1,grace)); return
    except subprocess.TimeoutExpired: pass
    try:
        if os.name=='nt': process.kill()
        else: os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError,OSError): pass

def main(argv=None):
    a=parser().parse_args(argv); command=a.command[1:] if a.command[:1]==['--'] else a.command
    if not command: print('FAIL no command supplied',file=sys.stderr); return 2
    if a.timeout<=0 or a.grace<=0 or a.tail_lines<1 or a.max_buffer_bytes<4096: print('FAIL invalid execution limits',file=sys.stderr); return 2
    print(f'==> {a.label} (timeout {a.timeout:g}s)',flush=True)
    chunks=deque(); buffered=0; lock=threading.Lock(); verbose=os.environ.get('HARNESS_VERBOSE')=='1'
    flags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name=='nt' else 0
    try: process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=os.name!='nt',creationflags=flags)
    except OSError as exc: print(f'FAIL {a.label}: {exc}',file=sys.stderr); return 127
    def reader():
        nonlocal buffered
        assert process.stdout is not None
        while True:
            block=process.stdout.read(8192)
            if not block: break
            if verbose: sys.stdout.buffer.write(block); sys.stdout.buffer.flush()
            with lock:
                chunks.append(block); buffered+=len(block)
                while chunks and buffered>a.max_buffer_bytes: buffered-=len(chunks.popleft())
    thread=threading.Thread(target=reader,daemon=True); thread.start(); started=time.monotonic(); timed_out=False; heartbeat=started+30
    while process.poll() is None:
        elapsed=time.monotonic()-started
        if elapsed>=a.timeout: timed_out=True; terminate_tree(process,a.grace); break
        if time.monotonic()>=heartbeat: print(f'RUNNING {a.label} ({elapsed:.0f}s)',flush=True); heartbeat+=30
        time.sleep(min(.2,max(.01,a.timeout-elapsed)))
    try: process.wait(timeout=max(.1,a.grace))
    except subprocess.TimeoutExpired: terminate_tree(process,a.grace)
    thread.join(timeout=max(1,a.grace)); elapsed=time.monotonic()-started
    with lock:
        text=b''.join(chunks).decode('utf-8',errors='replace'); lines=text.splitlines()
    if len(lines)>a.tail_lines: lines=[f'... output truncated; showing last {a.tail_lines} lines ...',*lines[-a.tail_lines:]]
    tail='\n'.join(lines)
    if timed_out:
        if tail and not verbose: print(tail,file=sys.stderr)
        print(f'TIMEOUT {a.label} after {elapsed:.1f}s',file=sys.stderr); return 124
    code=process.returncode if process.returncode is not None else 125
    if code==0: print(f'PASS {a.label} ({elapsed:.1f}s)'); return 0
    if tail and not verbose: print(tail,file=sys.stderr)
    print(f'FAIL {a.label} (exit {code}, {elapsed:.1f}s)',file=sys.stderr); return code if 0<code<126 else 1
if __name__=='__main__': raise SystemExit(main())
