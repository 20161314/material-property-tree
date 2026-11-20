"""Regression tests for source-asset collections miscounted as single objects."""
import unittest
from object_boundary_contract_v24 import audit_boundaries

class BoundaryContractTests(unittest.TestCase):
    def row(self, **updates):
        row = dict(source_uid='one', boundary_class='SINGLE_PRIMARY_OBJECT',
                   primary_object_count='1', source_metadata_locator='frozen.json#one',
                   visual_locator='contact.png#one', excluded_scope='Background excluded.',
                   geometry_membership_verified='false', decision='APPROVE_SOURCE_IDENTITY')
        row.update(updates)
        return row

    def test_source_uid_does_not_override_bundle(self):
        result = audit_boundaries([{'source_uid': 'one'}], [self.row(boundary_class='MULTI_OBJECT_BUNDLE')])
        self.assertTrue(result['errors'])

    def test_three_independent_swords_are_not_one(self):
        result = audit_boundaries([{'source_uid': 'one'}], [self.row(primary_object_count='3')])
        self.assertTrue(result['errors'])

    def test_functional_assembly_can_pass_without_claiming_mesh_validation(self):
        result = audit_boundaries([{'source_uid': 'one'}], [self.row(boundary_class='SINGLE_FUNCTIONAL_ASSEMBLY')])
        self.assertFalse(result['errors'])
        self.assertFalse(result['global_geometry_deduplication_proved'])

    def test_missing_or_duplicate_review_fails(self):
        self.assertTrue(audit_boundaries([{'source_uid': 'one'}], [])['errors'])
        self.assertTrue(audit_boundaries([{'source_uid': 'one'}], [self.row(), self.row()])['errors'])

    def test_unsupported_mesh_claim_fails(self):
        result = audit_boundaries([{'source_uid': 'one'}], [self.row(geometry_membership_verified='true')])
        self.assertIn('GEOMETRY_MEMBERSHIP_UNSUPPORTED:one', result['errors'])

    def test_material_pass_does_not_override_boundary_hold(self):
        result = audit_boundaries([{'source_uid': 'one', 'material_status': 'PASS'}], [self.row(decision='HOLD_OBJECT_BOUNDARY')])
        self.assertTrue(result['errors'])

    def test_missing_source_or_visual_locator_fails(self):
        for field in ('source_metadata_locator', 'visual_locator'):
            for value in (None, '', '   ', 'null', 'None', 'N/A'):
                with self.subTest(field=field, value=value):
                    result = audit_boundaries([{'source_uid': 'one'}], [self.row(**{field: value})])
                    self.assertTrue(result['errors'])

    def test_null_uid_cannot_form_an_approved_identity(self):
        result = audit_boundaries([{'source_uid': None}], [self.row(source_uid=None)])
        self.assertTrue(result['errors'])

    def test_geometry_evidence_locator_cannot_be_blank_or_placeholder(self):
        for value in (None, '', '   ', 'null', 'None', 'N/A'):
            with self.subTest(value=value):
                result = audit_boundaries([{'source_uid': 'one'}], [self.row(
                    geometry_membership_verified='true', geometry_membership_evidence_locator=value)])
                self.assertIn('GEOMETRY_MEMBERSHIP_UNSUPPORTED:one', result['errors'])

    def test_approval_prefix_does_not_accept_an_undeclared_decision(self):
        for decision in ('PASS_MATERIAL_ONLY_HOLD_BOUNDARY', 'APPROVED_FALSE', 'PASSIVE_HOLD', 'APPROVE_HOLD'):
            with self.subTest(decision=decision):
                result = audit_boundaries([{'source_uid': 'one', 'material_status': 'PASS'}], [self.row(decision=decision)])
                self.assertIn('BOUNDARY_NOT_APPROVED:one', result['errors'])

    def test_true_membership_with_locator_remains_structure_only(self):
        result = audit_boundaries([{'source_uid': 'one'}], [self.row(
            geometry_membership_verified='true', geometry_membership_evidence_locator='mesh_review.json#one')])
        self.assertFalse(result['errors'])
        self.assertEqual(result['status'], 'PASS_BOUNDARY_REVIEW_STRUCTURE_ONLY')
        self.assertTrue(result['independent_visual_review_required'])
        self.assertFalse(result['global_geometry_deduplication_proved'])

    def test_scoped_material_approval_exact_vocabulary_passes(self):
        result = audit_boundaries([{'source_uid': 'one'}], [self.row(decision='APPROVE_SOURCE_IDENTITY_SCOPED_MATERIAL')])
        self.assertFalse(result['errors'])

if __name__ == '__main__':
    unittest.main()
