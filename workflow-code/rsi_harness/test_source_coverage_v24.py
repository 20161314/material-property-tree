import csv
import tempfile
import unittest
from pathlib import Path

from source_coverage_v24 import family_for


class SourceCoverageV24Tests(unittest.TestCase):
    def test_required_family_mapping(self):
        self.assertEqual(family_for("VoMP GVM public preprocessed set (simready)"), "VoMP_GVM")
        self.assertEqual(family_for("PIXIEVerse public release (Objaverse source asset)"), "PIXIEVerse")
        self.assertEqual(family_for("PHYSXNET-FINALINDEX"), "PhysX_3D")
        self.assertEqual(family_for("PHYSX-MOBILITY"), "PhysX_Mobility")
        self.assertEqual(family_for("ABO 3D 模型商品"), "ABO")
        self.assertEqual(family_for("NVIDIA SimReady Assets official Hugging Face release"), "NVIDIA_SimReady")
        self.assertEqual(family_for("3DCoMPaT++ official semantic parts"), "3DCoMPaT_PLUSPLUS")
        self.assertEqual(family_for("GoogleResearch Scanned Objects (official Fuel release)"), "GSO")
        self.assertEqual(family_for("Objaverse-LVIS official asset metadata; cycle13"), "OBJAVERSE_SUPPLEMENTAL")
        self.assertEqual(family_for("YCB Object and Model Set official mesh table"), "YCB")

    def test_unknown_dataset_is_not_silently_promoted(self):
        self.assertEqual(family_for("unregistered visual dataset"), "OTHER")

class CoverageFreshnessTests(unittest.TestCase):
    def fixture(self, root):
        import json
        from source_coverage_v24 import (OBJECT_REL, MATERIAL_REL, SCOPE_POLICY_REL,
            REGISTRY_REL, MATRIX_REL, EVIDENCE_REL, SUMMARY_REL)
        def table(rel, rows):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader(); writer.writerows(rows)
        table(OBJECT_REL, [dict(object_id='O1', component_id='C1', source_dataset='Objaverse official frozen LVIS; batch',
            material_node_id='M1', material_identity_status='FORMAL_SOURCE'),
            dict(object_id='O1', component_id='C2', source_dataset='unregistered visual dataset',
            material_node_id='UNMAPPED', material_identity_status='HOLD')])
        table(MATERIAL_REL, [dict(material_id='M1')])
        table(REGISTRY_REL, [dict(dataset_id='source')])
        table(MATRIX_REL, [dict(source='source')])
        table(EVIDENCE_REL, [dict(E_low_GPa='1', nu_low='0.3', rho_low_kg_m3='1000'),
                             dict(E_low_GPa='', nu_low='', rho_low_kg_m3='1100')])
        (root / SCOPE_POLICY_REL).write_text(json.dumps({'excluded_material_ids': []}))
        summary = dict(object_identities=1, distinct_component_pairs=2, state_rows=2,
            material_nodes=1, main_source_groups=2, main_complete_groups=1, main_partial_groups=1)
        (root / SUMMARY_REL).write_text(json.dumps(summary))
        return summary

    def test_current_report_recomputes_and_unknown_family_remains_visible(self):
        from source_coverage_v24 import build_report, validate_report
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); summary=self.fixture(root); report=build_report(root)
            self.assertEqual(validate_report(root, report, summary), [])
            self.assertEqual(report['summary_counts'], summary)
            self.assertEqual(report['unclassified_source_dataset_rows'], {'unregistered visual dataset': 1})
            self.assertEqual(next(r for r in report['families'] if r['family']=='OBJAVERSE_SUPPLEMENTAL')['inventory_rows'],1)

    def test_old_report_without_provenance_is_rejected(self):
        from source_coverage_v24 import build_report, validate_report
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); summary=self.fixture(root); report=build_report(root)
            report.pop('input_sha256'); report['rules_version']='2.4.1'
            self.assertTrue(validate_report(root, report, summary))

    def test_value_change_with_identical_row_count_is_rejected(self):
        from source_coverage_v24 import build_report, validate_report, EVIDENCE_REL
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); summary=self.fixture(root); report=build_report(root)
            path=root/EVIDENCE_REL; path.write_text(path.read_text().replace('1100','1200'))
            self.assertTrue(any('input changed' in x for x in validate_report(root,report,summary)))

    def test_stale_summary_count_cannot_generate_pass_report(self):
        from source_coverage_v24 import build_report, SUMMARY_REL
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); summary=self.fixture(root); summary['object_identities']=7
            (root/SUMMARY_REL).write_text(__import__('json').dumps(summary))
            with self.assertRaises(ValueError): build_report(root)

    def test_summary_override_does_not_read_old_count_snapshot(self):
        from source_coverage_v24 import build_report, SUMMARY_REL, validate_report
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); summary=self.fixture(root)
            old=dict(summary,main_source_groups=100)
            (root/SUMMARY_REL).write_text(__import__('json').dumps(old))
            report=build_report(root,summary_override=summary)
            self.assertEqual(validate_report(root,report,summary),[])
            self.assertNotEqual(validate_report(root,report,old),[])
            self.assertNotIn(str(SUMMARY_REL),report['input_sha256'])

    def test_unsafe_report_pin_is_rejected(self):
        from source_coverage_v24 import build_report, validate_report
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); summary=self.fixture(root); report=build_report(root)
            report['input_sha256']['../outside']='a'*64
            self.assertTrue(any('unsafe' in x for x in validate_report(root,report,summary)))

    def test_unverified_alias_collapse_is_rejected(self):
        from source_coverage_v24 import build_report
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); summary=self.fixture(root)
            summary['raw_inventory_object_id_aliases_collapsed']=1
            with self.assertRaises(ValueError):build_report(root,summary_override=summary)

    def test_frozen_lvis_names_retain_supplemental_source_family(self):
        self.assertEqual(family_for('Objaverse official frozen LVIS; round3'), 'OBJAVERSE_SUPPLEMENTAL')


if __name__ == "__main__":
    unittest.main()
