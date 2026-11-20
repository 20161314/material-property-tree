import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import harness
from runtime_v23 import apply_schema, create_scan, seed_scan_frontier
from verify_snapshot_v23 import verify


class SnapshotPinTests(unittest.TestCase):
    def test_snapshot_pointer_pins_release_epochs_and_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            database = folder / "shadow.sqlite"
            db = harness.connect(database)
            apply_schema(db)
            for key, value in (("release_id", "r1"), ("rsi_shadow_parent_release_id", "r1"),
                               ("rsi_shadow_schema", "2.3"), ("rsi_shadow_snapshot_id", "test"),
                               ("epoch", "data1")):
                harness.set_meta(db, key, value)
            db.execute("INSERT INTO objects VALUES(?,?,?,?,?,?,?,?,?,?)",
                       ("o1", "PIXIEVERSE", "uid1", "name", "name", "", "", None, 1, "{}"))
            db.execute("INSERT INTO object_aliases VALUES(?,?,?,?,?)",
                       ("SLATPHYS", "uid1", "o1", "reviewed source UID alias", 1))
            create_scan(db, "scan1", "MIXED", "data1", "tree1", 10, 120, now=1)
            seed_scan_frontier(db, "scan1", [dict(lane="MATERIAL", task_type="MATERIAL_OPTIONAL_RESEARCH",
                subject_id="m1", state=4, attribute_scope="E", family="wood")], "data1", "tree1", now=1)
            db.close()
            digest = hashlib.sha256(database.read_bytes()).hexdigest()
            pointer = {"snapshot_id": "test", "database": database.name, "database_sha256": digest,
                       "source_release_id": "r1", "data_epoch": "data1", "tree_epoch": "tree1",
                       "scan": {"scan_id": "scan1", "routes": 1},
                       "counts": {"source_identities": 1, "components": 0, "material_nodes": 0},
                       "material_states": {}, "alias_counts": {"SLATPHYS": 1},
                       "reviewed_alias_counts": {"SLATPHYS": 1}}
            pointer_path = folder / "pointer.json"
            pointer_path.write_text(json.dumps(pointer))
            result = verify(pointer_path)
            self.assertEqual(result["status"], "PASS_V23_SNAPSHOT_PIN")
            self.assertEqual(result["alias_counts"], {"SLATPHYS": 1})
            pointer["alias_counts"] = {"SLATPHYS": 2}
            pointer_path.write_text(json.dumps(pointer))
            with self.assertRaisesRegex(ValueError, "source alias counts"):
                verify(pointer_path)
            pointer["alias_counts"] = {"SLATPHYS": 1}
            pointer["snapshot_id"] = "wrong-snapshot"
            pointer_path.write_text(json.dumps(pointer))
            with self.assertRaisesRegex(ValueError, "snapshot ID"):
                verify(pointer_path)
            pointer["snapshot_id"] = "test"
            pointer["source_release_id"] = "wrong"
            pointer_path.write_text(json.dumps(pointer))
            with self.assertRaisesRegex(ValueError, "parent release"):
                verify(pointer_path)


if __name__ == "__main__":
    unittest.main()
