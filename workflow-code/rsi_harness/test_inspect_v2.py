"""Isolated behavior checks for pinned, read-only, bounded RSI inspection."""
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import harness as h
import inspect_v2 as inspector


class InspectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name) / 'harness'
        self.directory.mkdir()
        for name in ('SPEC.md', 'harness.py', 'schema.sql', 'import_snapshot.py'):
            shutil.copyfile(h.HERE / name, self.directory / name)
        self.database = self.directory / 'fixture.sqlite'
        db = h.connect(self.database)
        db.execute("INSERT INTO nodes(id,name_cn,name_en,kind) VALUES('material','材料','Material','MATERIAL')")
        db.execute("INSERT INTO objects VALUES('object','source','uid','物体','Object','source','asset',NULL,1,'{}')")
        db.execute("INSERT INTO components VALUES('object','whole','WHOLE','whole','source','{}')")
        db.execute("INSERT INTO material_links VALUES('link','object','whole','material','whole','DIRECT','',1,'source','{}')")
        h.set_meta(db, 'inputs', {})
        self.epoch = h.recompute(db)['epoch']
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        db.close()
        self.snapshot = self.directory / 'CURRENT_SNAPSHOT.json'
        self.repin()

    def tearDown(self):
        self.temp.cleanup()

    def repin(self):
        self.snapshot.write_text(json.dumps({'database': self.database.name, 'database_sha256': inspector.sha(self.database),
                                             'snapshot_id': 'fixture', 'epoch': self.epoch}))

    def test_summary_is_bounded_and_database_stays_unchanged(self):
        before = inspector.sha(self.database)
        result = inspector.inspect(self.snapshot, 1, True)
        self.assertEqual(result['states'], {'3': 1})
        self.assertEqual(result['existing_object_material_coverage'], {'covered': 0, 'required': 1, 'percent': 0.0})
        self.assertEqual(len(result['queue_samples']['existing_object_material_gaps']), 1)
        self.assertEqual(result['queue_samples']['existing_object_material_gaps'][0]['missing_properties'], ['E', 'nu', 'rho'])
        self.assertEqual(inspector.sha(self.database), before)

    def test_changed_database_is_rejected(self):
        db = sqlite3.connect(self.database)
        db.execute("UPDATE nodes SET name_en='changed'")
        db.commit()
        db.close()
        with self.assertRaisesRegex(ValueError, 'SHA'):
            inspector.inspect(self.snapshot)

    def test_repin_cannot_hide_stale_facts(self):
        db = sqlite3.connect(self.database)
        db.execute("UPDATE nodes SET name_en='changed'")
        db.commit()
        db.close()
        self.repin()
        with self.assertRaisesRegex(ValueError, 'Facts changed'):
            inspector.inspect(self.snapshot)

    def test_changed_runtime_is_rejected(self):
        with (self.directory / 'schema.sql').open('a') as output:
            output.write('\n-- changed\n')
        with self.assertRaisesRegex(ValueError, 'implementation changed'):
            inspector.inspect(self.snapshot)

    def test_upstream_pin_requires_real_file(self):
        db = h.connect(self.database)
        h.set_meta(db, 'inputs', {'missing.csv': '0' * 64})
        self.epoch = h.recompute(db)['epoch']
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        db.close()
        self.repin()
        with self.assertRaisesRegex(ValueError, 'Upstream input changed'):
            inspector.inspect(self.snapshot, verify_inputs=True)

    def test_invalid_limit_rejected(self):
        for limit in (-1, 0, 51):
            with self.assertRaises(ValueError):
                inspector.inspect(self.snapshot, limit)

    def test_uncheckpointed_wal_is_rejected_even_when_main_sha_matches(self):
        before = inspector.sha(self.database)
        writer = sqlite3.connect(self.database)
        try:
            writer.execute('PRAGMA journal_mode=WAL')
            writer.execute('PRAGMA wal_autocheckpoint=0')
            writer.execute('UPDATE material_state SET state=1')
            writer.commit()
            self.assertEqual(inspector.sha(self.database), before)
            self.assertGreater(Path(str(self.database) + '-wal').stat().st_size, 0)
            with self.assertRaisesRegex(ValueError, 'nonempty SQLite sidecar'):
                inspector.inspect(self.snapshot)
        finally:
            writer.close()

    def test_nonempty_rollback_journal_is_rejected(self):
        journal = Path(str(self.database) + '-journal')
        journal.write_bytes(b'pending rollback journal')
        with self.assertRaisesRegex(ValueError, 'nonempty SQLite sidecar'):
            inspector.inspect(self.snapshot)

    def test_writer_appearing_during_inspection_is_rejected(self):
        original = inspector.sealed_identity
        calls = []
        def racing_identity(database, expected_sha):
            calls.append(None)
            if len(calls) == 2:
                Path(str(database) + '-wal').write_bytes(b'new uncheckpointed transaction')
            return original(database, expected_sha)
        with patch.object(inspector, 'sealed_identity', side_effect=racing_identity):
            with self.assertRaisesRegex(ValueError, 'nonempty SQLite sidecar'):
                inspector.inspect(self.snapshot)

    def test_same_byte_database_replacement_during_read_is_rejected(self):
        original = inspector.sealed_identity
        calls = []
        def replaced_identity(database, expected_sha):
            calls.append(None)
            if len(calls) == 2:
                replacement = self.directory / 'replacement.sqlite'
                replacement.write_bytes(database.read_bytes())
                replacement.replace(database)
            return original(database, expected_sha)
        with patch.object(inspector, 'sealed_identity', side_effect=replaced_identity):
            with self.assertRaisesRegex(ValueError, 'changed during inspection'):
                inspector.inspect(self.snapshot)


if __name__ == '__main__':
    unittest.main()
