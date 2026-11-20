import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT = ROOT / "audit/object_material_cycle5_sync_2026-11-13/verify_current_delivery.py"
DIAGNOSTIC = ROOT / "audit/object_material_cycle5_sync_2026-11-13/verify_current_delivery_QA.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RetiredCycle5ValidatorTests(unittest.TestCase):
    def test_old_validator_fails_closed_and_preserves_qa(self):
        before = sha(DIAGNOSTIC)
        result = subprocess.run(
            [sys.executable, str(ENTRYPOINT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "RETIRED_RELEASE_SCOPED_VALIDATOR")
        self.assertFalse(payload["historical_output_writes"])
        self.assertEqual(sha(DIAGNOSTIC), before)

    def test_original_validator_source_is_archived(self):
        archive = ROOT / (
            "audit/rsi_framework_review_2026-11-15/"
            "legacy_cycle5_verify_current_delivery_2026-11-13.source.txt"
        )
        self.assertTrue(archive.is_file())
        self.assertGreater(archive.stat().st_size, 10_000)


if __name__ == "__main__":
    unittest.main()
