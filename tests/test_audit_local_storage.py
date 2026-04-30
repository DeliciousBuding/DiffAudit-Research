from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "audit_local_storage", root / "scripts" / "audit_local_storage.py"
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


audit_local_storage = _load_module()


class AuditLocalStorageTests(unittest.TestCase):
    def test_collect_blocks_tracked_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Research"
            source = root / "workspaces" / "gray-box" / "assets" / "pia" / "sources"
            source.mkdir(parents=True)
            (source / "tracked.bin").write_bytes(b"x")
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(
                ["git", "add", "workspaces/gray-box/assets/pia/sources/tracked.bin"],
                cwd=root,
                check=True,
                stdout=subprocess.DEVNULL,
            )

            candidates, _external = audit_local_storage.collect_candidates(
                root, min_mb=0, archive_subdir="test"
            )

        candidate = next(c for c in candidates if c.source.endswith("pia/sources"))
        self.assertEqual(candidate.action, "blocked_tracked_files")
        self.assertEqual(candidate.tracked_files, 1)

    def test_execute_rolls_back_when_link_creation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Research"
            source = root / "outputs" / "sample"
            source.mkdir(parents=True)
            (source / "payload.bin").write_bytes(b"x")
            archive_root = root.parent / "Archive" / "research-local-artifacts" / "test"
            target = archive_root / "outputs" / "sample"
            candidate = audit_local_storage.MoveCandidate(
                category="cache_tmp",
                source="outputs/sample",
                target=str(target),
                size_mb=0.0,
                tracked_files=0,
                action="move_and_link",
                reason="test",
            )

            original_make_link = audit_local_storage._make_link
            audit_local_storage._make_link = lambda _source, _target: (_ for _ in ()).throw(
                OSError("link failed")
            )
            try:
                with self.assertRaises(OSError):
                    audit_local_storage._execute_candidate(root, candidate, archive_root)
            finally:
                audit_local_storage._make_link = original_make_link

            self.assertTrue(source.exists())
            self.assertFalse(target.exists())

    def test_size_bytes_prunes_directory_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = root / "payload"
            external = root / "external"
            payload.mkdir()
            external.mkdir()
            (payload / "kept.bin").write_bytes(b"a" * 3)
            (external / "ignored.bin").write_bytes(b"b" * 100)
            link = payload / "linked"
            try:
                link.symlink_to(external, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"directory symlink unavailable: {exc}")

            self.assertEqual(audit_local_storage._size_bytes(payload), 3)


if __name__ == "__main__":
    unittest.main()
