#!/usr/bin/env python3
"""Functional regression tests for Harness runtime mechanics."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import copy
import contextlib
import io
import os
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "scripts" / "bridge.py"
SAFE_EXEC = ROOT / "scripts" / "safe_exec.py"
PROJECT_CHECKS = ROOT / "scripts" / "project_checks.py"
BRIDGE_MODULE = None


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_bridge(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        global BRIDGE_MODULE
        if BRIDGE_MODULE is None:
            BRIDGE_MODULE = load_module("bridge_runtime_tests", BRIDGE)
        stdout, stderr = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = BRIDGE_MODULE.main(["--root", str(self.root), *arguments])
        except SystemExit as exc:
            code = int(exc.code or 0)
        return subprocess.CompletedProcess(arguments, code, stdout.getvalue(), stderr.getvalue())

    def test_claim_conflict_release_and_board(self) -> None:
        self.assertEqual(self.run_bridge("init").returncode, 0)
        first = self.run_bridge("log", "run-1", "writer-a", "claim", "task", "own module", "src/**")
        self.assertEqual(first.returncode, 0, first.stderr)
        conflict = self.run_bridge("log", "run-2", "writer-b", "claim", "task", "overlap", "src/app.py")
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("claim conflict", conflict.stderr)
        release = self.run_bridge("log", "run-1", "writer-a", "release", "task", "released", "src/**")
        self.assertEqual(release.returncode, 0, release.stderr)
        second = self.run_bridge("log", "run-2", "writer-b", "claim", "task", "now free", "src/app.py")
        self.assertEqual(second.returncode, 0, second.stderr)
        board = (self.root / "docs" / "ai" / "bridge" / "board.md").read_text(encoding="utf-8")
        self.assertIn("src/app.py", board)
        self.assertNotIn("src/**` | run-1", board)

    def test_read_commands_do_not_mutate_bridge_files(self) -> None:
        self.assertEqual(self.run_bridge("init").returncode, 0)
        ledger = self.root / "docs" / "ai" / "bridge" / "ledger.jsonl"
        board = ledger.parent / "board.md"
        before = (ledger.stat().st_mtime_ns, board.stat().st_mtime_ns, ledger.read_bytes(), board.read_bytes())
        for command in (("tail", "15"), ("claims",), ("board",), ("doctor",)):
            result = self.run_bridge(*command)
            self.assertEqual(result.returncode, 0, result.stderr)
        after = (ledger.stat().st_mtime_ns, board.stat().st_mtime_ns, ledger.read_bytes(), board.read_bytes())
        self.assertEqual(before, after)

    def test_note_limit_and_legacy_read(self) -> None:
        too_long = self.run_bridge("log", "run", "actor", "note", "task", "x" * 141)
        self.assertNotEqual(too_long.returncode, 0)
        ledger = self.root / "docs" / "ai" / "bridge" / "ledger.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text(
            json.dumps({"ts": "2026-01-01T00:00Z", "a": "legacy-agent", "e": "claim", "t": "old", "f": ["legacy/**"], "n": "v1"}) + "\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_bridge("init").returncode, 0)
        claims = self.run_bridge("claims")
        self.assertEqual(claims.returncode, 0, claims.stderr)
        self.assertIn("legacy/**", claims.stdout)
        doctor = self.run_bridge("doctor")
        self.assertEqual(doctor.returncode, 0, doctor.stderr)
        self.assertIn("1 legacy events", doctor.stdout)

    def test_rejects_injection_negative_lease_and_case_alias(self) -> None:
        self.assertEqual(self.run_bridge("init").returncode, 0)
        injected = self.run_bridge("log", "run", "actor", "note", "task", "safe\n| FAKE |")
        self.assertNotEqual(injected.returncode, 0)
        negative = self.run_bridge("log", "run", "actor", "claim", "task", "bad lease", "src/x.py", "", "-1")
        self.assertNotEqual(negative.returncode, 0)
        first = self.run_bridge("log", "run-a", "writer-a", "claim", "task", "case owner", "Src/App.py")
        self.assertEqual(first.returncode, 0, first.stderr)
        alias = self.run_bridge("log", "run-b", "writer-b", "claim", "task", "case alias", "src/app.py")
        self.assertNotEqual(alias.returncode, 0)
        self.assertIn("claim conflict", alias.stderr)
        release = self.run_bridge("log", "run-a", "writer-a", "release", "task", "case release", "src/app.py")
        self.assertEqual(release.returncode, 0, release.stderr)
        claimed = self.run_bridge("log", "run-b", "writer-b", "claim", "task", "now free", "src/app.py")
        self.assertEqual(claimed.returncode, 0, claimed.stderr)
        html_note = self.run_bridge("log", "run-b", "writer-b", "progress", "task", "<img src=x>")
        self.assertEqual(html_note.returncode, 0, html_note.stderr)
        board = self.run_bridge("board")
        self.assertIn("&lt;img src=x&gt;", board.stdout)

    def test_invalid_ledger_blocks_writes(self) -> None:
        ledger = self.root / "docs" / "ai" / "bridge" / "ledger.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "v": 2,
            "id": "00000000-0000-4000-8000-000000000001",
            "ts": "2026-01-01T00:00:00Z",
            "run": "run",
            "a": "actor",
            "e": "note",
            "t": "task",
            "f": [],
            "n": "duplicate",
            "nx": "",
            "lease": None,
        }
        ledger.write_text(json.dumps(event) + "\n" + json.dumps(event) + "\n", encoding="utf-8")
        write = self.run_bridge("log", "run", "actor", "note", "task", "must fail")
        self.assertNotEqual(write.returncode, 0)
        self.assertIn("ledger is invalid", write.stderr)

    def test_live_lock_is_not_stolen(self) -> None:
        bridge = load_module("bridge_lock_test", BRIDGE)
        paths = bridge.bridge_paths(self.root)
        bridge.ensure_files(paths)
        paths["lock"].write_text(
            json.dumps({"pid": os.getpid(), "host": socket.gethostname(), "token": "live-token", "created": "2000-01-01T00:00:00Z"}),
            encoding="utf-8",
        )
        old = time.time() - 120
        os.utime(paths["lock"], (old, old))
        with self.assertRaises(bridge.BridgeError):
            with bridge.bridge_lock(paths, timeout=0.1):
                pass
        self.assertTrue(paths["lock"].exists())

    @unittest.skipUnless(os.name == "nt", "Windows-specific process probe regression")
    def test_windows_process_probe_does_not_call_os_kill(self) -> None:
        bridge = load_module("bridge_windows_probe_test", BRIDGE)
        with mock.patch.object(bridge.os, "kill", side_effect=AssertionError("os.kill must not probe Windows processes")):
            self.assertTrue(bridge.process_alive(os.getpid()))

    def test_compaction_preserves_active_claim_run_and_blocker(self) -> None:
        ledger = self.root / "docs" / "ai" / "bridge" / "ledger.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        events: list[dict] = []
        for index in range(205):
            event = {
                "v": 2,
                "id": f"00000000-0000-4000-8000-{index:012d}",
                "ts": f"2026-01-01T00:{index % 60:02d}:00Z",
                "run": "run",
                "a": "actor",
                "e": (
                    "claim"
                    if index == 0
                    else "start"
                    if index == 1
                    else "blocked"
                    if index == 2
                    else "handoff"
                    if index == 3
                    else "note"
                ),
                "t": "task",
                "f": ["kept/**"] if index == 0 else [],
                "n": f"event {index}",
                "nx": "",
                "lease": "2099-01-01T00:00:00Z" if index == 0 else None,
            }
            events.append(event)
        ledger.write_text("".join(json.dumps(event, separators=(",", ":")) + "\n" for event in events), encoding="utf-8")
        self.assertEqual(self.run_bridge("init").returncode, 0)
        compact = self.run_bridge("compact")
        self.assertEqual(compact.returncode, 0, compact.stderr)
        self.assertIn("including active claims", compact.stdout)
        self.assertIn("kept/**", self.run_bridge("claims").stdout)
        retained = ledger.read_text(encoding="utf-8").splitlines()
        archived = (ledger.parent / "ledger-archive.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(retained), 103)
        self.assertEqual(len(archived), 102)
        board = (ledger.parent / "board.md").read_text(encoding="utf-8")
        self.assertIn("run", board)
        self.assertIn("event 2", board)


class ExecutionGuardTests(unittest.TestCase):
    def test_safe_exec_times_out_and_terminates(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SAFE_EXEC), "--label", "timeout-test", "--timeout", "0.2", "--grace", "0.1", "--", sys.executable, "-c", "import time; time.sleep(5)"],
            text=True,
            capture_output=True,
            check=False,
            timeout=5,
            env={key: value for key, value in os.environ.items() if key != "HARNESS_VERBOSE"},
        )
        self.assertEqual(result.returncode, 124, result.stdout + result.stderr)
        self.assertIn("TIMEOUT timeout-test", result.stderr)

    def test_safe_exec_bounds_failure_output(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SAFE_EXEC), "--label", "tail-test", "--tail-lines", "5", "--", sys.executable, "-c", "import sys; [print(i) for i in range(50)]; sys.exit(7)"],
            text=True,
            capture_output=True,
            check=False,
            timeout=5,
            env={key: value for key, value in os.environ.items() if key != "HARNESS_VERBOSE"},
        )
        self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
        self.assertIn("output truncated", result.stderr)
        self.assertNotIn("\n0\n", result.stderr)


class ProjectChecksTests(unittest.TestCase):
    def test_discovers_immediate_child_npm_projects(self) -> None:
        checks = load_module("project_checks_discovery_test", PROJECT_CHECKS)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, scripts in (
                ("api", {"lint": "eslint .", "test": "vitest run"}),
                ("frontend", {"build": "vite build"}),
            ):
                project = root / name
                project.mkdir()
                (project / "package.json").write_text(
                    json.dumps({"scripts": scripts}), encoding="utf-8"
                )
            with mock.patch.object(checks, "ROOT", root):
                projects = checks.package_projects()
            self.assertEqual(
                [path.name for path, _scripts in projects], ["api", "frontend"]
            )

    def test_nested_npm_command_uses_prefix(self) -> None:
        checks = load_module("project_checks_command_test", PROJECT_CHECKS)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "api"
            project.mkdir()
            with (
                mock.patch.object(checks, "ROOT", root),
                mock.patch.object(checks, "npm_executable", return_value="npm.cmd"),
            ):
                command = checks.npm_command(project, "run", "lint")
            self.assertEqual(
                command, ["npm.cmd", "--prefix", "api", "run", "lint"]
            )

    def test_filtered_tests_use_nested_npm_project(self) -> None:
        checks = load_module("project_checks_filter_test", PROJECT_CHECKS)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "api"
            project.mkdir()
            (project / "package.json").write_text(
                json.dumps({"scripts": {"test": "vitest run"}}), encoding="utf-8"
            )
            with (
                mock.patch.object(checks, "ROOT", root),
                mock.patch.object(checks, "SAFE", root / "scripts" / "safe_exec.py"),
                mock.patch.object(checks, "npm_executable", return_value="npm.cmd"),
                mock.patch.object(checks, "run", return_value=0) as run,
                mock.patch.dict(os.environ, {"HARNESS_NPM_TEST_FILTERS": "auth-plan discovery"}),
            ):
                result = checks.check_test()
            self.assertEqual(result, (1, 0))
            self.assertEqual(
                run.call_args.args[1],
                ["npm.cmd", "--prefix", "api", "test", "--", "auth-plan", "discovery"],
            )

    def test_security_includes_product_boundary_scripts(self) -> None:
        checks = load_module("project_checks_security_test", PROJECT_CHECKS)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / "scripts"
            scripts.mkdir()
            for name in ("check-n8n-security.mjs", "check-systemd-security.mjs"):
                (scripts / name).write_text("", encoding="utf-8")
            with (
                mock.patch.object(checks, "ROOT", root),
                mock.patch.object(checks, "node_executable", return_value="node.exe"),
                mock.patch.object(checks, "npm_executable", return_value=None),
                mock.patch.object(checks.shutil, "which", return_value=None),
                mock.patch.object(checks, "run", return_value=0) as run,
            ):
                ran, incomplete = checks.check_security()
            self.assertEqual(ran, 2)
            self.assertGreater(incomplete, 0)
            commands = [call.args[1] for call in run.call_args_list]
            self.assertIn(["node.exe", str(scripts / "check-n8n-security.mjs")], commands)
            self.assertIn(["node.exe", str(scripts / "check-systemd-security.mjs")], commands)


class PackageTests(unittest.TestCase):
    @unittest.skipUnless((ROOT / "scaffold").is_dir(), "maintainer-source package test")
    def test_package_is_deterministic_and_clean(self) -> None:
        package = load_module("package_runtime", ROOT / "scripts" / "package_runtime.py")
        first_payload, manifest = package.build_payload(ROOT)
        package.validate_payload(first_payload, manifest)
        first = package.archive_bytes(first_payload, manifest)
        second_payload, second_manifest = package.build_payload(ROOT)
        second = package.archive_bytes(second_payload, second_manifest)
        self.assertEqual(hashlib.sha256(first).digest(), hashlib.sha256(second).digest())
        self.assertEqual(first_payload["docs/ai/bridge/ledger.jsonl"], b"")
        self.assertFalse(any(name.startswith("docs/ai/tasks/2026-") for name in first_payload))
        self.assertFalse(any(name.startswith("scaffold/") for name in first_payload))
        self.assertNotIn("README.md", first_payload)
        self.assertNotIn("CHANGELOG.md", first_payload)
        self.assertNotIn(".harness-source", first_payload)

    @unittest.skipUnless((ROOT / "scaffold").is_dir(), "maintainer-source package test")
    def test_package_rejects_external_sensitive_and_wrong_output(self) -> None:
        package = load_module("package_security", ROOT / "scripts" / "package_runtime.py")
        _, manifest = package.build_payload(ROOT)
        with tempfile.TemporaryDirectory() as temp_name, tempfile.TemporaryDirectory() as outside_name:
            temp_root = Path(temp_name)
            outside = Path(outside_name)
            (outside / "secret.txt").write_text("secret", encoding="utf-8")
            with self.assertRaises(package.PackageError):
                package.add_tree({}, temp_root, outside, "")
            source = temp_root / "source"
            source.mkdir()
            (source / ".env.production").write_text("TOKEN=secret", encoding="utf-8")
            with self.assertRaises(package.PackageError):
                package.add_tree({}, temp_root, source, "")
            internal = temp_root / "internal"
            internal.mkdir()
            linked = temp_root / "linked"
            try:
                linked.symlink_to(internal, target_is_directory=True)
            except OSError:
                pass
            else:
                with self.assertRaises(package.PackageError):
                    package.add_tree({}, temp_root, linked, "")
            output = temp_root / manifest["distribution"]["archive"]
            package.write_atomic(output, b"first")
            with self.assertRaises(package.PackageError):
                package.write_atomic(output, b"second")
            self.assertEqual(output.read_bytes(), b"first")
        with self.assertRaises(package.PackageError):
            package.safe_output(ROOT, Path("AGENTS.md"), manifest)

    @unittest.skipUnless((ROOT / "scaffold").is_dir(), "maintainer-source package test")
    def test_archive_validator_rejects_traversal_directory(self) -> None:
        package = load_module("package_for_zip_test", ROOT / "scripts" / "package_runtime.py")
        runtime = load_module("runtime_for_zip_test", ROOT / "scripts" / "runtime_check.py")
        payload, manifest = package.build_payload(ROOT)
        with tempfile.TemporaryDirectory() as temp_name:
            archive = Path(temp_name) / "agent-runtime-v4.2.zip"
            archive.write_bytes(package.archive_bytes(payload, manifest))
            with zipfile.ZipFile(archive, "a") as handle:
                info = zipfile.ZipInfo("../../escape/", date_time=(2026, 7, 15, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (stat.S_IFDIR | 0o755) << 16
                handle.writestr(info, b"")
            report = runtime.Report()
            runtime.archive_checks(ROOT, archive, manifest, report)
            self.assertTrue(report.failures)

    @unittest.skipUnless((ROOT / "scaffold").is_dir(), "maintainer-source package test")
    def test_clean_distribution_validates_with_unrelated_scaffold_directory(self) -> None:
        package = load_module("package_extract_test", ROOT / "scripts" / "package_runtime.py")
        payload, manifest = package.build_payload(ROOT)
        with tempfile.TemporaryDirectory() as temp_name:
            destination = Path(temp_name)
            archive = destination / "runtime.zip"
            archive.write_bytes(package.archive_bytes(payload, manifest))
            extracted = destination / "extracted"
            with zipfile.ZipFile(archive) as handle:
                handle.extractall(extracted)
            (extracted / "scaffold").mkdir()
            result = subprocess.run(
                [sys.executable, str(extracted / "scripts" / "runtime_check.py"), "--root", str(extracted), "--static"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(importlib.util.find_spec("jsonschema") is not None, "release jsonschema dependency")
    def test_json_schemas_reject_invalid_contract_fixtures(self) -> None:
        import jsonschema

        checker = jsonschema.FormatChecker()
        schemas = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in (ROOT / "schemas").glob("*.schema.json")}
        task = json.loads((ROOT / "docs" / "ai" / "tasks" / "_TASK_CONTRACT_TEMPLATE.task.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schemas["task-contract.schema.json"], format_checker=checker).validate(task)
        bad_task = copy.deepcopy(task)
        bad_task["mode"] = "review"
        bad_task["authorization"]["writes"]["allowed"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schemas["task-contract.schema.json"], format_checker=checker).validate(bad_task)
        done_without_evidence = copy.deepcopy(task)
        done_without_evidence["status"] = "done"
        done_without_evidence["validation"]["evidence"] = []
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schemas["task-contract.schema.json"], format_checker=checker).validate(done_without_evidence)

        gate = json.loads((ROOT / "docs" / "ai" / "tasks" / "_GATE_RESULT_TEMPLATE.json").read_text(encoding="utf-8"))
        bad_gate = copy.deepcopy(gate)
        bad_gate["status"] = "passed"
        bad_gate["applicability"]["applicable"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schemas["gate-result.schema.json"], format_checker=checker).validate(bad_gate)

        invalid_bridge = {
            "v": 2,
            "id": "00000000-0000-4000-8000-000000000001",
            "ts": "2026-01-01T00:00:00Z",
            "run": "run",
            "a": "actor",
            "e": "claim",
            "t": "task",
            "f": ["src/x.py"],
            "n": "claim",
            "nx": "",
            "lease": None,
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schemas["bridge-event.schema.json"], format_checker=checker).validate(invalid_bridge)

        bad_manifest = json.loads((ROOT / "harness.json").read_text(encoding="utf-8"))
        bad_manifest["released"] = "not-a-date"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schemas["harness.schema.json"], format_checker=checker).validate(bad_manifest)

    def test_static_runtime_check(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "runtime_check.py"), "--root", str(ROOT), "--static"],
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("powershell.exe") is not None, "PowerShell unavailable")
    def test_powershell_propagates_child_failure(self) -> None:
        missing = ROOT / "definitely-missing-runtime-root"
        script_arg = str(ROOT / "scripts" / "run.ps1")
        missing_arg = str(missing)
        if os.name != "nt" and shutil.which("wslpath"):
            script_arg = subprocess.check_output(["wslpath", "-w", script_arg], text=True).strip()
            missing_arg = subprocess.check_output(["wslpath", "-w", missing_arg], text=True).strip()
        result = subprocess.run(
            [
                shutil.which("powershell.exe"),
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                script_arg,
                "runtime",
                "--root",
                missing_arg,
                "--static",
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
