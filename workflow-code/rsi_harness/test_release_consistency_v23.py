import unittest

from verify_release_consistency_v23 import verify


class ReleaseConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.release = {
            "id": "r1",
            "objects": {"total": 10, "components": 20, "rows": 25},
            "materials": {"total": 4},
            "records": {"complete": 7, "partial": 8, "total": 15,
                        "main": {"complete": 3, "incomplete": 2}},
        }
        self.download = {
            "release_id": "r1",
            "objects": {"total": 10, "components": 20, "rows": 25},
            "materials": {"total": 4},
            "records": {"complete": 7, "partial": 8, "total": 15,
                        "main": {"complete": 3, "incomplete": 2}},
        }
        self.summary = {"object_identities": 10, "distinct_component_pairs": 20,
                        "state_rows": 25, "material_nodes": 4,
                        "main_complete_groups": 3, "main_partial_groups": 2,
                        "main_source_groups": 5}

    def test_consistent_same_release_views_pass(self):
        result = verify(self.release, self.download, self.summary, self.summary)
        self.assertEqual(result["status"], "PASS_RELEASE_COUNTS_CONSISTENT")
        self.assertEqual(result["errors"], [])

    def test_stale_summary_counts_fail_closed(self):
        stale = dict(self.summary, object_identities=9, material_nodes=3)
        result = verify(self.release, self.download, stale, self.summary)
        self.assertEqual(result["status"], "FAIL_RELEASE_COUNTS_INCONSISTENT")
        self.assertEqual(len(result["errors"]), 2)

    def test_release_identity_mismatch_fails(self):
        result = verify(self.release, dict(self.download, release_id="old"),
                        self.summary, self.summary)
        self.assertTrue(any("release_id" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
