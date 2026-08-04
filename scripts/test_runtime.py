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
SECURITY_ASSURANCE = ROOT / "scripts" / "security_assurance.py"
UI_QUALITY = ROOT / "scripts" / "ui_quality.py"
ADVERSARIAL_LAB = ROOT / "scripts" / "adversarial_lab.py"
ARCHITECTURE_CHECK = ROOT / "scripts" / "architecture_check.py"
BOOTSTRAP_PROJECT = ROOT / "scripts" / "bootstrap_project.py"
ADOPT_HARNESS = ROOT / "scripts" / "adopt_harness.py"
AUTOMATION_DECISION = ROOT / "scripts" / "automation_decision.py"
DOCUMENTATION_CHECK = ROOT / "scripts" / "documentation_check.py"
GUARDRAILS = ROOT / "scripts" / "harnesslib" / "guardrails.py"
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
            [sys.executable, "-B", str(SAFE_EXEC), "--label", "timeout-test", "--timeout", "0.2", "--grace", "0.1", "--", sys.executable, "-B", "-c", "import time; time.sleep(5)"],
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
            [sys.executable, "-B", str(SAFE_EXEC), "--label", "tail-test", "--tail-lines", "5", "--", sys.executable, "-B", "-c", "import sys; [print(i) for i in range(50)]; sys.exit(7)"],
            text=True,
            capture_output=True,
            check=False,
            timeout=5,
            env={key: value for key, value in os.environ.items() if key != "HARNESS_VERBOSE"},
        )
        self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
        self.assertIn("output truncated", result.stderr)
        self.assertNotIn("\n0\n", result.stderr)

    def test_environment_sanitizer_removes_secret_named_values(self) -> None:
        guardrails = load_module("guardrails_environment_test", GUARDRAILS)
        sanitized = guardrails.sanitize_environment(
            {
                "PATH": "safe-path",
                "SESSION_TOKEN": "synthetic-secret",
                "UNRELATED": "not-forwarded",
            },
            ["PATH", "SESSION_TOKEN", "UNRELATED"],
            r"(?i)(secret|token|password|session)",
        )
        self.assertEqual(sanitized["PATH"], "safe-path")
        self.assertNotIn("SESSION_TOKEN", sanitized)
        self.assertEqual(sanitized["UNRELATED"], "not-forwarded")
        self.assertEqual(sanitized["CI"], "1")


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
                mock.patch.object(
                    checks,
                    "limits",
                    return_value={
                        "default_command_timeout_seconds": 300,
                        "kill_grace_seconds": 5,
                        "failure_tail_lines": 120,
                        "max_output_buffer_bytes": 262144,
                    },
                ),
                mock.patch.object(checks, "run", return_value=0) as run,
                mock.patch.dict(os.environ, {"HARNESS_NPM_TEST_FILTERS": "auth-plan discovery"}),
            ):
                result = checks.check_test(trusted=True, allow_secret_env=False)
            self.assertEqual(result, (1, 0))
            self.assertEqual(
                run.call_args.args[1],
                ["npm.cmd", "--prefix", "api", "test", "--", "auth-plan", "discovery"],
            )

    def test_untrusted_project_test_is_not_executed(self) -> None:
        checks = load_module("project_checks_trust_test", PROJECT_CHECKS)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text(
                json.dumps({"scripts": {"test": "node exfiltrate.js"}}),
                encoding="utf-8",
            )
            with (
                mock.patch.object(checks, "ROOT", root),
                mock.patch.object(checks, "run", side_effect=AssertionError("must not run")),
            ):
                ran, incomplete = checks.check_test(
                    trusted=False, allow_secret_env=False
                )
            self.assertEqual((ran, incomplete), (0, 1))

    def test_security_uses_bundled_assurance_without_project_script_execution(self) -> None:
        checks = load_module("project_checks_security_test", PROJECT_CHECKS)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / "scripts"
            scripts.mkdir()
            for name in ("check-n8n-security.mjs", "check-systemd-security.mjs"):
                (scripts / name).write_text("", encoding="utf-8")
            with (
                mock.patch.object(checks, "ROOT", root),
                mock.patch.object(
                    checks,
                    "limits",
                    return_value={
                        "default_command_timeout_seconds": 300,
                        "kill_grace_seconds": 5,
                        "failure_tail_lines": 120,
                        "max_output_buffer_bytes": 262144,
                    },
                ),
                mock.patch.object(checks, "run", return_value=0) as run,
            ):
                ran, incomplete = checks.check_security(external=False)
            self.assertEqual((ran, incomplete), (1, 0))
            commands = [call.args[1] for call in run.call_args_list]
            self.assertEqual(len(commands), 1)
            self.assertIn(str(root / "scripts" / "security_assurance.py"), commands[0])
            self.assertNotIn(str(scripts / "check-n8n-security.mjs"), commands[0])
            self.assertNotIn(str(scripts / "check-systemd-security.mjs"), commands[0])


class SecurityAndUiTests(unittest.TestCase):
    def test_stale_next_and_node_are_release_blockers(self) -> None:
        security = load_module("security_stale_runtime_test", SECURITY_ASSURANCE)
        reporting = load_module(
            "security_reporting_test", ROOT / "scripts" / "harnesslib" / "reporting.py"
        )
        policy = json.loads((ROOT / "security-policy.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "dependencies": {"next": "14.2.1"},
                        "engines": {"node": "20.x"},
                    }
                ),
                encoding="utf-8",
            )
            (root / "package-lock.json").write_text(
                json.dumps(
                    {
                        "lockfileVersion": 3,
                        "packages": {"node_modules/next": {"version": "14.2.1"}},
                    }
                ),
                encoding="utf-8",
            )
            (root / ".nvmrc").write_text("20\n", encoding="utf-8")
            report = reporting.CheckReport("stale")
            security.check_node_projects(root, policy, "release", report)
        joined = "\n".join(report.failures)
        self.assertIn("outside supported policy majors", joined)
        self.assertIn("unsupported major", joined)

    def test_current_next_and_node_meet_lifecycle_floor(self) -> None:
        security = load_module("security_current_runtime_test", SECURITY_ASSURANCE)
        reporting = load_module(
            "security_current_reporting_test",
            ROOT / "scripts" / "harnesslib" / "reporting.py",
        )
        policy = json.loads((ROOT / "security-policy.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "dependencies": {"next": "16.2.11"},
                        "engines": {"node": "24.x"},
                    }
                ),
                encoding="utf-8",
            )
            (root / "package-lock.json").write_text(
                json.dumps(
                    {
                        "lockfileVersion": 3,
                        "packages": {"node_modules/next": {"version": "16.2.11"}},
                    }
                ),
                encoding="utf-8",
            )
            (root / ".nvmrc").write_text("24\n", encoding="utf-8")
            report = reporting.CheckReport("current")
            security.check_node_projects(root, policy, "ci", report)
        self.assertFalse(report.failures)
        self.assertTrue(any("meets the dated security floor" in item for item in report.passes))

    def test_incomplete_ui_contract_cannot_pass_release(self) -> None:
        ui = load_module("ui_incomplete_contract_test", UI_QUALITY)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "schemas").mkdir()
            shutil.copy2(
                ROOT / "schemas" / "ui-review.schema.json",
                root / "schemas" / "ui-review.schema.json",
            )
            (root / "docs" / "ai").mkdir(parents=True)
            (root / "package.json").write_text(
                json.dumps({"dependencies": {"next": "16.2.11"}}), encoding="utf-8"
            )
            (root / "docs" / "ai" / "ui-review.json").write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "status": "approved",
                        "applicability": {"applicable": True, "reason": "web UI"},
                    }
                ),
                encoding="utf-8",
            )
            with contextlib.redirect_stderr(io.StringIO()):
                result = ui.main(["--root", str(root), "--profile", "release"])
        self.assertNotEqual(result, 0)

    def test_adversarial_plan_rejects_ambiguous_and_external_unscoped_targets(self) -> None:
        lab = load_module("adversarial_scope_test", ADVERSARIAL_LAB)
        base = {
            "target_origin": "http://127.0.0.1:8080",
            "max_requests": 1,
            "scenarios": [
                {
                    "id": "probe",
                    "method": "GET",
                    "path": "//attacker.invalid",
                    "required_headers": [],
                    "forbidden_body_markers": [],
                }
            ],
        }
        with self.assertRaises(ValueError):
            lab.canonical_plan(base)
        encoded = copy.deepcopy(base)
        encoded["scenarios"][0]["path"] = "/allowed/%2e%2e/admin"
        with self.assertRaises(ValueError):
            lab.canonical_plan(encoded)
        external = copy.deepcopy(base)
        external["target_origin"] = "http://192.0.2.1"
        external["scenarios"][0]["path"] = "/"
        with self.assertRaises(ValueError):
            lab.prepare_execution(ROOT, external, None)

    def test_authorized_path_prefix_has_a_segment_boundary(self) -> None:
        guardrails = load_module("guardrails_prefix_test", GUARDRAILS)
        self.assertTrue(guardrails.path_is_allowed("/api/orders", ["/api"]))
        self.assertTrue(guardrails.path_is_allowed("/api", ["/api"]))
        self.assertFalse(guardrails.path_is_allowed("/api-evil", ["/api"]))


class HybridEngineeringTests(unittest.TestCase):
    def run_script(self, script: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(script), *arguments],
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )

    def bootstrap(self, target: Path) -> None:
        plan = self.run_script(BOOTSTRAP_PROJECT, "plan", "--target", str(target))
        self.assertEqual(plan.returncode, 0, plan.stdout + plan.stderr)
        applied = self.run_script(BOOTSTRAP_PROJECT, "apply", "--target", str(target))
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)

    def test_bootstrap_is_plan_first_complete_and_non_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            target = Path(temp_name)
            self.bootstrap(target)
            self.assertTrue((target / "backend" / "app" / "services").is_dir())
            self.assertTrue((target / "frontend" / "src" / "components" / "ui").is_dir())
            self.assertTrue((target / "SOURCE-OF-TRUTH.md").is_file())
            protected = target / "backend" / "README.md"
            protected.write_text("user-owned\n", encoding="utf-8")
            blocked = self.run_script(BOOTSTRAP_PROJECT, "apply", "--target", str(target))
            self.assertEqual(blocked.returncode, 3, blocked.stdout + blocked.stderr)
            self.assertEqual(protected.read_text(encoding="utf-8"), "user-owned\n")
            merged = self.run_script(
                BOOTSTRAP_PROJECT,
                "apply",
                "--target",
                str(target),
                "--skip-existing",
            )
            self.assertEqual(merged.returncode, 3, merged.stdout + merged.stderr)
            self.assertEqual(protected.read_text(encoding="utf-8"), "user-owned\n")

    def test_bootstrap_rejects_unsafe_template_path(self) -> None:
        bootstrap = load_module("bootstrap_path_test", BOOTSTRAP_PROJECT)
        with self.assertRaises(bootstrap.BootstrapError):
            bootstrap.portable_path("../../escape.txt")
        with self.assertRaises(bootstrap.BootstrapError):
            bootstrap.portable_path("C:\\escape.txt")

    def test_architecture_accepts_thin_entrypoints_and_documented_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            target = Path(temp_name)
            self.bootstrap(target)
            valid = self.run_script(ARCHITECTURE_CHECK, "--root", str(target), "--profile", "ci")
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
            extension = target / "frontend" / "src" / "features"
            extension.mkdir()
            invalid = self.run_script(ARCHITECTURE_CHECK, "--root", str(target), "--profile", "ci")
            self.assertEqual(invalid.returncode, 1, invalid.stdout + invalid.stderr)
            directory_map = target / "docs" / "architecture" / "DIRECTORY-MAP.md"
            directory_map.write_text(
                directory_map.read_text(encoding="utf-8")
                + "\n| `frontend/src/features/` | Feature modules | declared public layers |\n",
                encoding="utf-8",
            )
            documented = self.run_script(ARCHITECTURE_CHECK, "--root", str(target), "--profile", "ci")
            self.assertEqual(documented.returncode, 0, documented.stdout + documented.stderr)

    def test_architecture_rejects_backend_routes_and_frontend_transport_in_entrypoints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            target = Path(temp_name)
            self.bootstrap(target)
            (target / "backend" / "app" / "main.py").write_text(
                "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/orders')\ndef orders():\n    return []\n",
                encoding="utf-8",
            )
            (target / "frontend" / "src" / "App.tsx").write_text(
                "export function App(){ fetch('/api/orders'); return <main /> }\n",
                encoding="utf-8",
            )
            result = self.run_script(ARCHITECTURE_CHECK, "--root", str(target), "--profile", "ci")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("defines HTTP route", result.stdout)
            self.assertIn("feature or transport behavior", result.stdout)

    def test_release_documentation_blocks_templates_and_accepts_initialized_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            target = Path(temp_name)
            self.bootstrap(target)
            blocked = self.run_script(DOCUMENTATION_CHECK, "--root", str(target), "--profile", "release")
            self.assertEqual(blocked.returncode, 1, blocked.stdout + blocked.stderr)
            replacements = {
                "Status: UNINITIALIZED": "Status: CURRENT",
                "Status: DRAFT": "Status: CURRENT",
                "uninitialized": "current",
                "not set": "2026-08-03",
                "<PROJECT_NAME>": "Example",
                "<PROJECT_PURPOSE>": "Example purpose",
                "<VERSION>": "1.0.0",
                "<OWNER>": "Example owner",
                "<DATE>": "2026-08-03",
                "<AUDIENCE>": "Example users",
            }
            for relative in ("SOURCE-OF-TRUTH.md", "docs/TECHNICAL-DOCUMENTATION.md", "docs/USER-MANUAL.md"):
                path = target / relative
                text = path.read_text(encoding="utf-8")
                for old, new in replacements.items():
                    text = text.replace(old, new)
                path.write_text(text, encoding="utf-8")
            passed = self.run_script(DOCUMENTATION_CHECK, "--root", str(target), "--profile", "release")
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)


class AdoptionAndAutomationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        package = load_module("package_for_adoption_tests", ROOT / "scripts" / "package_runtime.py")
        cls.payload, cls.manifest = package.build_payload(ROOT)
        package.validate_payload(cls.payload, cls.manifest)
        cls.adopt = load_module("adopt_harness_tests", ADOPT_HARNESS)

    def write_distribution(self, root: Path) -> None:
        for name, content in self.payload.items():
            path = root / Path(*name.split("/"))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

    def source_data(self, root: Path) -> dict:
        self.write_distribution(root)
        return self.adopt.verify_source(root)

    def test_automation_contract_accepts_draft_hybrid_and_rejects_pure_n8n_blocker(self) -> None:
        example = ROOT / "docs" / "harness" / "examples" / "automation-decision.example.json"
        valid = subprocess.run(
            [sys.executable, "-B", str(AUTOMATION_DECISION), str(example)],
            text=True, capture_output=True, check=False, timeout=30,
        )
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        decision = json.loads(example.read_text(encoding="utf-8"))
        decision["execution_plane"] = "n8n"
        decision["blocker_handling"] = []
        with tempfile.TemporaryDirectory() as temp_name:
            invalid_path = Path(temp_name) / "invalid.json"
            invalid_path.write_text(json.dumps(decision), encoding="utf-8")
            invalid = subprocess.run(
                [sys.executable, "-B", str(AUTOMATION_DECISION), str(invalid_path)],
                text=True, capture_output=True, check=False, timeout=30,
            )
        self.assertEqual(invalid.returncode, 1, invalid.stdout + invalid.stderr)
        self.assertIn("FAIL automation decision", invalid.stderr)

    def test_brownfield_plan_is_read_only_preserves_stack_and_skips_target_policy(self) -> None:
        with tempfile.TemporaryDirectory() as source_name, tempfile.TemporaryDirectory() as target_name:
            source = Path(source_name)
            target = Path(target_name)
            source_data = self.source_data(source)
            (target / "src").mkdir()
            (target / "src" / "server.js").write_text("existing\n", encoding="utf-8")
            (target / "package.json").write_text('{"name":"existing"}\n', encoding="utf-8")
            before = sorted(path.relative_to(target).as_posix() for path in target.rglob("*"))
            plan = self.adopt.build_plan(source_data, target, "auto")
            after = sorted(path.relative_to(target).as_posix() for path in target.rglob("*"))
            self.assertEqual(before, after)
            self.assertEqual(plan["adoption_mode"], "brownfield")
            self.assertEqual(plan["application_posture"], "observed")
            self.assertEqual(plan["architecture_disposition"], "profile_required")
            architecture = next(item for item in plan["operations"] if item["path"] == "docs/ai/architecture-policy.json")
            self.assertEqual(architecture["action"], "skip")
            self.assertFalse(any(item["path"].startswith(("backend/", "frontend/")) for item in plan["operations"]))
            self.assertFalse((target / ".harness").exists())

    def test_greenfield_apply_and_verify_do_not_bootstrap_application(self) -> None:
        with tempfile.TemporaryDirectory() as source_name, tempfile.TemporaryDirectory() as target_name:
            source, target = Path(source_name), Path(target_name)
            source_data = self.source_data(source)
            plan = self.adopt.build_plan(source_data, target, "greenfield")
            self.adopt.validate_plan(plan, source / "schemas" / "adoption-plan.schema.json")
            self.assertEqual(plan["status"], "ready")
            self.adopt.apply_plan(source_data, target, plan, approve_replace=False)
            self.assertEqual(self.adopt.verify_installation(source_data, target), [])
            self.assertTrue((target / ".harness" / "adoption-state.json").is_file())
            self.assertFalse((target / "backend").exists())
            self.assertFalse((target / "frontend").exists())

    def test_upgrade_requires_approval_backs_up_harness_and_preserves_project_memory(self) -> None:
        with tempfile.TemporaryDirectory() as source_name, tempfile.TemporaryDirectory() as target_name:
            source, target = Path(source_name), Path(target_name)
            source_data = self.source_data(source)
            prior = copy.deepcopy(source_data["harness"])
            prior["version"] = "6.0.0"
            for marker in (
                "scripts/runtime_check.py",
                ".agents/skills/core/task-triage/SKILL.md",
                "docs/harness/INSTALL.md",
            ):
                path = target / Path(*marker.split("/"))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("prior\n", encoding="utf-8")
            (target / "harness.json").write_text(json.dumps(prior), encoding="utf-8")
            truth = target / "SOURCE-OF-TRUTH.md"
            truth.write_text("project-owned truth\n", encoding="utf-8")
            plan = self.adopt.build_plan(source_data, target, "upgrade")
            self.assertEqual(plan["status"], "awaiting_approval")
            self.assertIn("replace_harness_owned", plan["approvals"])
            with self.assertRaises(self.adopt.AdoptionBlocked):
                self.adopt.apply_plan(source_data, target, plan, approve_replace=False)
            self.adopt.apply_plan(source_data, target, plan, approve_replace=True)
            self.assertEqual(truth.read_text(encoding="utf-8"), "project-owned truth\n")
            backup = target / ".harness" / "rollback" / plan["plan_digest"] / "harness.json"
            self.assertTrue(backup.is_file())
            self.assertEqual(self.adopt.verify_installation(source_data, target), [])

    def test_shared_conflict_and_target_drift_block_without_partial_writes(self) -> None:
        with tempfile.TemporaryDirectory() as source_name, tempfile.TemporaryDirectory() as target_name:
            source, target = Path(source_name), Path(target_name)
            source_data = self.source_data(source)
            (target / "AGENTS.md").write_text("project instructions\n", encoding="utf-8")
            conflict = self.adopt.build_plan(source_data, target, "brownfield")
            self.assertEqual(conflict["status"], "blocked")
            with self.assertRaises(self.adopt.AdoptionBlocked):
                self.adopt.apply_plan(source_data, target, conflict, approve_replace=False)
            self.assertFalse((target / "harness.json").exists())
            reconciled = self.adopt.build_plan(source_data, target, "brownfield", {"AGENTS.md"})
            self.assertEqual(reconciled["status"], "ready")
            self.assertEqual(reconciled["reconciled_shared"], ["AGENTS.md"])
            self.adopt.apply_plan(source_data, target, reconciled, approve_replace=False)
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "project instructions\n")
            self.assertEqual(self.adopt.verify_installation(source_data, target), [])

        with tempfile.TemporaryDirectory() as source_name, tempfile.TemporaryDirectory() as target_name:
            source, target = Path(source_name), Path(target_name)
            source_data = self.source_data(source)
            plan = self.adopt.build_plan(source_data, target, "greenfield")
            (target / "AGENTS.md").write_text("appeared after plan\n", encoding="utf-8")
            with self.assertRaises(self.adopt.AdoptionBlocked):
                self.adopt.apply_plan(source_data, target, plan, approve_replace=False)
            self.assertFalse((target / "harness.json").exists())

    def test_brownfield_architecture_is_incomplete_not_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            target = Path(temp_name)
            (target / "src").mkdir()
            (target / "package.json").write_text('{"name":"existing"}', encoding="utf-8")
            state = target / ".harness" / "adoption-state.json"
            state.parent.mkdir()
            state.write_text(json.dumps({"architecture_disposition": "profile_required", "application_posture": "observed"}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(ARCHITECTURE_CHECK), "--root", str(target)],
                text=True, capture_output=True, check=False, timeout=30,
            )
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("observed brownfield", result.stdout)

    def test_adoption_rejects_maintainer_source_and_unsafe_manifest_path(self) -> None:
        with self.assertRaises(self.adopt.AdoptionError):
            self.adopt.verify_source(ROOT)
        with tempfile.TemporaryDirectory() as source_name:
            source = Path(source_name)
            self.write_distribution(source)
            manifest = source / "MANIFEST.sha256"
            manifest.write_text(manifest.read_text(encoding="utf-8") + "0" * 64 + "  ../escape\n", encoding="utf-8")
            with self.assertRaises(self.adopt.AdoptionError):
                self.adopt.verify_source(source)


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

    def test_archive_validator_rejects_extreme_compression_ratio(self) -> None:
        runtime = load_module(
            "runtime_for_ratio_test", ROOT / "scripts" / "runtime_check.py"
        )
        manifest = json.loads((ROOT / "harness.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temp_name:
            archive = Path(temp_name) / "ratio.zip"
            with zipfile.ZipFile(
                archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
            ) as handle:
                handle.writestr("highly-repetitive.txt", b"A" * 1_048_576)
            report = runtime.Report()
            runtime.archive_checks(ROOT, archive, manifest, report)
        self.assertTrue(
            any("compression-ratio bounds" in item for item in report.failures)
        )

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
                [sys.executable, "-B", str(extracted / "scripts" / "runtime_check.py"), "--root", str(extracted), "--static"],
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

        architecture = json.loads((ROOT / "scaffold" / "docs" / "ai" / "architecture-policy.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schemas["architecture-policy.schema.json"], format_checker=checker).validate(architecture)
        bad_architecture = copy.deepcopy(architecture)
        bad_architecture["extensions"]["allow_additional_directories"] = False
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schemas["architecture-policy.schema.json"], format_checker=checker).validate(bad_architecture)

        template = json.loads((ROOT / "project-templates" / "python-react-hybrid" / "template-manifest.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schemas["project-template.schema.json"], format_checker=checker).validate(template)
        bad_template = copy.deepcopy(template)
        bad_template["minimum_directories"].append("../escape")
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schemas["project-template.schema.json"], format_checker=checker).validate(bad_template)

    def test_static_runtime_check(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts" / "runtime_check.py"), "--root", str(ROOT), "--static"],
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
