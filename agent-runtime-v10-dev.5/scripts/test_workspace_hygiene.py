"""Focused tests for reversible workspace hygiene."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("workspace_hygiene", ROOT / "scripts" / "workspace_hygiene.py")
assert SPEC and SPEC.loader
HYGIENE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HYGIENE)


class WorkspaceHygieneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "workspace"
        self.root.mkdir()
        self.policy = HYGIENE.load_policy(ROOT / "workspace-hygiene-policy.json")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, relative: str, content: str) -> Path:
        path = self.root / Path(*relative.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def plan(self, candidates: list[str], *, archive_id: str = "arc-20260831T020500Z-test", evidence: list[str] | None = None, retained_canonical: str | None = None) -> tuple[dict, Path]:
        plan_path = Path(self.temporary.name) / "selected.archive-plan.json"
        args = argparse.Namespace(
            candidate=candidates,
            evidence=evidence or ["owner_instruction"],
            confidence="high",
            owner="synthetic-test-owner",
            retained_canonical=retained_canonical,
            supersedes=[],
            reason="Owner approved archival of completed synthetic material.",
            slug="test",
            archive_id=archive_id,
            out=plan_path,
        )
        plan = HYGIENE.build_plan(args, self.root.resolve(), self.policy)
        HYGIENE.write_atomic(plan_path, plan)
        return plan, plan_path

    def test_inventory_uses_positive_signals_not_age_and_finds_duplicates(self) -> None:
        self.write("docs/current.md", "current")
        self.write("docs/copy-a.md", "duplicate")
        self.write("docs/copy-b.md", "duplicate")
        self.write("docs/ai/tasks/old.task.json", json.dumps({"status": "done"}))
        report = HYGIENE.inventory(self.root.resolve(), self.policy)
        states = {item["path"]: item["state"] for item in report["items"]}
        self.assertEqual(states["docs/current.md"], "active")
        self.assertEqual(states["docs/copy-b.md"], "archive_candidate")
        self.assertEqual(states["docs/ai/tasks/old.task.json"], "archive_candidate")
        self.assertFalse(report["automatic_purge"])
        self.assertEqual(report["active_discovery_excludes"], ["**/_archives/**/content/**"])

    def test_protected_authority_and_sensitive_files_are_rejected(self) -> None:
        self.write("AGENTS.md", "authority")
        self.write("notes/secrets.json", "{}")
        for candidate in ("AGENTS.md", "notes/secrets.json"):
            with self.subTest(candidate=candidate):
                with self.assertRaises(HYGIENE.HygieneError):
                    self.plan([candidate])

    def test_exact_duplicate_requires_matching_retained_canonical(self) -> None:
        self.write("docs/canonical.md", "same")
        self.write("docs/copy.md", "same")
        plan, _ = self.plan(["docs/copy.md"], evidence=["exact_duplicate"], retained_canonical="docs/canonical.md")
        self.assertEqual(plan["items"][0]["retained_canonical"], "docs/canonical.md")
        self.write("docs/not-same.md", "different")
        with self.assertRaisesRegex(HYGIENE.HygieneError, "not an exact duplicate"):
            self.plan(["docs/not-same.md"], evidence=["exact_duplicate"], retained_canonical="docs/canonical.md")

    def test_active_reference_blocks_plan(self) -> None:
        self.write("docs/old.md", "old")
        self.write("docs/current.md", "See docs/old.md")
        with self.assertRaisesRegex(HYGIENE.HygieneError, "active references"):
            self.plan(["docs/old.md"])

    def test_one_bundle_cannot_mix_ownership_boundaries(self) -> None:
        self.write("docs/a/old.md", "a")
        self.write("docs/b/old.md", "b")
        with self.assertRaisesRegex(HYGIENE.HygieneError, "one ownership boundary"):
            self.plan(["docs/a/old.md", "docs/b/old.md"])

    def test_plan_apply_verify_and_restore_round_trip(self) -> None:
        original = self.write("docs/design/old.md", "historical design")
        plan, plan_path = self.plan(["docs/design/old.md"])
        self.assertEqual(plan["archive_root"], "docs/design/_archives")
        self.assertTrue(original.is_file())
        manifest_path = HYGIENE.apply_plan(self.root.resolve(), self.policy, plan_path, "owner-approval-1")
        self.assertFalse(original.exists())
        self.assertEqual(HYGIENE.verify_manifest(self.root.resolve(), self.policy, manifest_path)["status"], "passed")
        inventory = HYGIENE.inventory(self.root.resolve(), self.policy)
        self.assertGreater(inventory["counts"]["archived"], 0)
        restored = HYGIENE.restore_manifest(self.root.resolve(), self.policy, manifest_path, "owner-restore-1")
        self.assertEqual(restored["status"], "restored")
        self.assertEqual(original.read_text(encoding="utf-8"), "historical design")
        events = (self.root / "docs/design/_archives/index.jsonl").read_text(encoding="utf-8")
        self.assertIn('"event": "archived"', events)
        self.assertIn('"event": "restored"', events)

    def test_plan_drift_blocks_before_any_move(self) -> None:
        source = self.write("docs/old.md", "first")
        _, plan_path = self.plan(["docs/old.md"])
        source.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(HYGIENE.HygieneError, "fingerprint changed"):
            HYGIENE.apply_plan(self.root.resolve(), self.policy, plan_path, "owner-approval-1")
        self.assertTrue(source.is_file())
        self.assertFalse((self.root / "docs/_archives").exists())

    def test_restore_never_overwrites_a_live_path(self) -> None:
        source = self.write("docs/old.md", "archived")
        _, plan_path = self.plan(["docs/old.md"])
        manifest_path = HYGIENE.apply_plan(self.root.resolve(), self.policy, plan_path, "owner-approval-1")
        source.write_text("new live content", encoding="utf-8")
        with self.assertRaisesRegex(HYGIENE.HygieneError, "restore collision"):
            HYGIENE.restore_manifest(self.root.resolve(), self.policy, manifest_path, "owner-restore-1")
        self.assertEqual(source.read_text(encoding="utf-8"), "new live content")

    def test_path_escape_and_overlapping_candidates_are_rejected(self) -> None:
        self.write("docs/group/a.md", "a")
        with self.assertRaises(HYGIENE.HygieneError):
            self.plan(["../outside.md"])
        with self.assertRaisesRegex(HYGIENE.HygieneError, "overlap"):
            self.plan(["docs/group", "docs/group/a.md"])

    def test_apply_rolls_back_completed_moves_after_partial_failure(self) -> None:
        first = self.write("docs/old-a.md", "a")
        second = self.write("docs/old-b.md", "b")
        _, plan_path = self.plan(["docs/old-a.md", "docs/old-b.md"])
        real_move = HYGIENE.shutil.move
        calls = 0

        def controlled_move(source: str, destination: str) -> str:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("synthetic second-move failure")
            return real_move(source, destination)

        with mock.patch.object(HYGIENE.shutil, "move", side_effect=controlled_move):
            with self.assertRaisesRegex(HYGIENE.HygieneError, "synthetic second-move failure"):
                HYGIENE.apply_plan(self.root.resolve(), self.policy, plan_path, "owner-approval-1")
        self.assertEqual(first.read_text(encoding="utf-8"), "a")
        self.assertEqual(second.read_text(encoding="utf-8"), "b")
        manifest = HYGIENE.load_json(self.root / "docs/_archives/arc-20260831T020500Z-test/archive-manifest.json")
        self.assertEqual(manifest["status"], "rolled_back")

    def test_tampered_destination_is_rejected_before_move(self) -> None:
        source = self.write("docs/old.md", "old")
        plan, plan_path = self.plan(["docs/old.md"])
        plan["items"][0]["destination"] = "docs/unreviewed-location.md"
        base = {key: value for key, value in plan.items() if key not in {"$schema", "plan_id"}}
        plan["plan_id"] = f"plan-{HYGIENE.hashlib.sha256(HYGIENE.json_bytes(base)).hexdigest()[:16]}"
        HYGIENE.write_atomic(plan_path, plan)
        with self.assertRaisesRegex(HYGIENE.HygieneError, "destination"):
            HYGIENE.apply_plan(self.root.resolve(), self.policy, plan_path, "owner-approval-1")
        self.assertTrue(source.is_file())
        self.assertFalse((self.root / "docs/unreviewed-location.md").exists())

    def test_index_failure_rolls_back_payload(self) -> None:
        source = self.write("docs/old.md", "old")
        _, plan_path = self.plan(["docs/old.md"])
        with mock.patch.object(HYGIENE, "append_jsonl_atomic", side_effect=OSError("synthetic index failure")):
            with self.assertRaisesRegex(HYGIENE.HygieneError, "synthetic index failure"):
                HYGIENE.apply_plan(self.root.resolve(), self.policy, plan_path, "owner-approval-1")
        self.assertEqual(source.read_text(encoding="utf-8"), "old")
        manifest = HYGIENE.load_json(self.root / "docs/_archives/arc-20260831T020500Z-test/archive-manifest.json")
        self.assertEqual(manifest["status"], "rolled_back")

    def test_restore_index_failure_returns_payload_to_archive(self) -> None:
        source = self.write("docs/old.md", "old")
        _, plan_path = self.plan(["docs/old.md"])
        manifest_path = HYGIENE.apply_plan(self.root.resolve(), self.policy, plan_path, "owner-approval-1")
        real_append = HYGIENE.append_jsonl_atomic

        def fail_restored_event(path: Path, value: object, max_bytes: int) -> None:
            if isinstance(value, dict) and value.get("event") == "restored":
                raise OSError("synthetic restore index failure")
            real_append(path, value, max_bytes)

        with mock.patch.object(HYGIENE, "append_jsonl_atomic", side_effect=fail_restored_event):
            with self.assertRaisesRegex(HYGIENE.HygieneError, "synthetic restore index failure"):
                HYGIENE.restore_manifest(self.root.resolve(), self.policy, manifest_path, "owner-restore-1")
        self.assertFalse(source.exists())
        manifest = HYGIENE.load_json(manifest_path)
        self.assertEqual(manifest["status"], "archived")
        self.assertEqual(manifest["restore"]["status"], "available")
        self.assertEqual(HYGIENE.verify_manifest(self.root.resolve(), self.policy, manifest_path)["status"], "passed")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support unavailable")
    def test_symlink_candidate_is_never_followed(self) -> None:
        outside = Path(self.temporary.name) / "outside.txt"
        outside.write_text("outside", encoding="utf-8")
        link = self.root / "link.txt"
        try:
            link.symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"symlink creation unavailable: {exc}")
        with self.assertRaises(HYGIENE.HygieneError):
            self.plan(["link.txt"])
        self.assertEqual(outside.read_text(encoding="utf-8"), "outside")

    @unittest.skipUnless(os.name == "nt", "Windows junction behavior")
    def test_windows_junction_candidate_and_nested_boundary_are_rejected(self) -> None:
        outside = Path(self.temporary.name) / "outside-directory"
        outside.mkdir()
        (outside / "outside.txt").write_text("outside", encoding="utf-8")
        direct = self.root / "direct-junction"
        bundle = self.root / "bundle"
        bundle.mkdir()
        nested = bundle / "nested-junction"

        def create_junction(link: Path) -> None:
            quoted_link = str(link).replace("'", "''")
            quoted_target = str(outside).replace("'", "''")
            result = subprocess.run(
                [
                    "powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                    f"New-Item -ItemType Junction -Path '{quoted_link}' -Target '{quoted_target}' | Out-Null",
                ],
                text=True, capture_output=True, check=False, timeout=30,
            )
            if result.returncode != 0:
                self.skipTest(f"junction creation unavailable: {result.stderr.strip()}")

        create_junction(direct)
        create_junction(nested)
        with self.assertRaises(HYGIENE.HygieneError):
            self.plan(["direct-junction"])
        with self.assertRaisesRegex(HYGIENE.HygieneError, "contains a link"):
            self.plan(["bundle"])
        self.assertEqual((outside / "outside.txt").read_text(encoding="utf-8"), "outside")


if __name__ == "__main__":
    unittest.main(verbosity=2)
