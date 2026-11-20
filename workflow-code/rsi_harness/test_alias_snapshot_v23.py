import unittest
from collections import Counter

from repair_alias_snapshot_v23 import require_unstarted_scan, task_signature


class AliasSnapshotRepairTests(unittest.TestCase):
    def test_material_queue_signature_matches_seeded_route_contract(self):
        task = {"lane": "MATERIAL", "task_type": "MATERIAL_VALUE_REPAIR",
                "material_id": "mat1", "attribute_scope": "E", "priority": 0,
                "depth": 2, "family": "textile"}
        self.assertEqual(task_signature(task), (
            "MATERIAL|MATERIAL_VALUE_REPAIR|mat1|E", "initial", "MATERIAL",
            "MATERIAL_VALUE_REPAIR", "mat1", "E", 0, 2, "textile", 0,
        ))

    def test_object_repair_signature_binds_component_and_obligation(self):
        task = {"lane": "OBJECT", "task_type": "OBJECT_LABEL_REPAIR",
                "object_id": "obj1", "subject_id": "obj1", "component_id": "cmp1",
                "obligation_id": "obl1", "attribute_scope": "NONE", "priority": -1,
                "depth": 0, "family": "existing-object-repair", "existing_object": True}
        self.assertEqual(task_signature(task)[0],
                         "OBJECT|OBJECT_LABEL_REPAIR|obj1|NONE|cmp1|obl1")

    def test_alias_snapshot_fork_requires_unspent_unstarted_scan(self):
        scan = {"status": "READY", "claims_spent": 0, "seconds_spent": 0.0,
                "budget_revision": 0}
        require_unstarted_scan(scan, Counter({"PENDING": 2}), False)
        with self.assertRaisesRegex(ValueError, "spend or budget history"):
            require_unstarted_scan({**scan, "claims_spent": 1}, Counter({"PENDING": 2}), False)
        with self.assertRaisesRegex(ValueError, "route history"):
            require_unstarted_scan(scan, Counter({"DONE": 1, "PENDING": 1}), False)
        with self.assertRaisesRegex(ValueError, "active run"):
            require_unstarted_scan(scan, Counter({"PENDING": 2}), True)


if __name__ == "__main__":
    unittest.main()
