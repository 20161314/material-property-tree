"""Small adversarial fixtures for fixed scale counts and persistent BFS migration."""
import copy
import unittest

from contracts_v22 import configuration_key, delivery_summary, migrate_frontier


def object_row(uid='a', geometry='g', config=None):
    row = dict(release_id='fixture-v1', accepted=True, namespace='fixture', source_uid=uid,
               geometry_id=geometry, dedup_reviewed=True, name_cn='夹具对象', name_en='Fixture object',
               source_url='fixture://source/' + uid, asset_url='fixture://bundle',
               asset_member_locator=uid + '.glb', license_status='FIXTURE', access_status='LOCATABLE',
               asset_location_verified=True, configuration_kind='BASE',
               component_kinds=['SEMANTIC'], source_scope_complete=True,
               component_readiness_basis='source explicitly lists its scope',
               unresolved_component_obligations=0, required_material_ids=['wood'],
               covered_material_ids=['wood'], unresolved_material_obligations=0)
    if config is not None:
        row.update(configuration_kind='EXPLICIT', configuration_reviewed=True,
                   configuration_basis='source-defined configuration', configuration_resolved=True,
                   configuration_materials=[dict(scope_id='body', material_id=config)])
        row.update(required_material_ids=[config], covered_material_ids=[config])
    return row


class DeliveryContracts(unittest.TestCase):
    def test_base_and_its_configurations_are_not_added(self):
        out = delivery_summary([object_row(), object_row('b', config='wood'), object_row('c', config='metal')])
        self.assertEqual((out['N'], out['G'], out['S'], out['explicit_configurations']), (2, 1, 3, 2))

    def test_cross_source_same_configuration_deduplicates(self):
        rows = [object_row('a', config='wood'), object_row('b', config='wood')]
        rows[1]['namespace'] = 'other'
        self.assertEqual(delivery_summary(rows)['N'], 1)

    def test_configuration_order_does_not_change_key(self):
        row = object_row(config='wood')
        row['configuration_materials'].append(dict(scope_id='seat', material_id='fabric'))
        other = copy.deepcopy(row)
        other['configuration_materials'].reverse()
        self.assertEqual(configuration_key(row), configuration_key(other))

    def test_scoped_material_swap_is_a_different_configuration(self):
        row = object_row(config='wood')
        other = copy.deepcopy(row)
        other['configuration_materials'][0]['scope_id'] = 'seat'
        self.assertNotEqual(configuration_key(row), configuration_key(other))

    def test_unresolved_alternatives_cannot_multiply_objects(self):
        row = object_row(config='wood')
        row['configuration_resolved'] = False
        with self.assertRaisesRegex(ValueError, 'Unresolved'):
            delivery_summary([row])

    def test_unreviewed_geometry_is_provisional(self):
        row = object_row()
        row['dedup_reviewed'] = False
        out = delivery_summary([row])
        self.assertEqual((out['N'], out['U_source_identities']), (0, 1))

    def test_missing_asset_member_is_not_deliverable(self):
        row = object_row()
        row['asset_member_locator'] = ''
        with self.assertRaisesRegex(ValueError, 'asset_member_locator'):
            delivery_summary([row])

    def test_asset_location_requires_actual_projection_verification(self):
        row = object_row()
        row['asset_location_verified'] = False
        with self.assertRaisesRegex(ValueError, 'Asset location'):
            delivery_summary([row])

    def test_whole_needs_positive_single_scope_evidence(self):
        row = object_row()
        row['component_kinds'] = ['WHOLE']
        self.assertEqual(delivery_summary([row])['R'], 0)
        row['whole_scope_positive'] = True
        self.assertEqual(delivery_summary([row])['R'], 1)
        row['unresolved_component_obligations'] = 1
        self.assertEqual(delivery_summary([row])['R'], 0)

    def test_all_material_options_must_be_covered(self):
        row = object_row()
        row['required_material_ids'] = ['wood', 'metal']
        self.assertEqual(delivery_summary([row])['C'], 0)
        row['covered_material_ids'].append('metal')
        self.assertEqual(delivery_summary([row])['C'], 1)

    def test_empty_materials_do_not_pass(self):
        row = object_row()
        row['required_material_ids'] = []
        self.assertEqual(delivery_summary([row])['C'], 0)

    def test_duplicate_source_cannot_hide_unresolved_obligations(self):
        a, b = object_row('a'), object_row('b')
        b['unresolved_material_obligations'] = 1
        b['component_kinds'] = ['UNCLASSIFIED']
        out = delivery_summary([a, b])
        self.assertEqual((out['N'], out['R'], out['C'], out['RC']), (1, 0, 0, 0))

    def test_base_scope_obligations_not_discarded_by_variant(self):
        base = object_row()
        base['unresolved_component_obligations'] = 1
        out = delivery_summary([base, object_row('b', config='wood')])
        self.assertEqual((out['N'], out['R'], out['RC']), (1, 0, 0))

    def test_mixed_release_rejected(self):
        a, b = object_row(), object_row('b')
        b['release_id'] = 'other-version'
        with self.assertRaisesRegex(ValueError, 'mixed releases'):
            delivery_summary([a, b])

    def test_zero_cohort_does_not_report_complete(self):
        out = delivery_summary([])
        self.assertFalse(out['all_components_ready'])
        self.assertFalse(out['all_properties_ready'])

    def test_temperature_and_source_do_not_create_configuration(self):
        a, b = object_row('a', config='wood'), object_row('b', config='wood')
        b['temperature'] = 70
        b['asset_url'] = 'fixture://other-file'
        self.assertEqual(delivery_summary([a, b])['N'], 1)

    def test_configuration_materials_are_required_even_when_caller_omits_them(self):
        row = object_row(config='metal')
        row.update(required_material_ids=['wood'], covered_material_ids=['wood'])
        out = delivery_summary([row])
        self.assertEqual((out['C'], out['RC']), (0, 0))

    def test_source_identity_cannot_claim_two_canonical_geometries(self):
        with self.assertRaisesRegex(ValueError, 'conflicting canonical geometries'):
            delivery_summary([object_row('same', 'g1'), object_row('same', 'g2')])

    def test_blank_material_ids_cannot_cover_unknown_labels(self):
        row = object_row()
        row.update(required_material_ids=[''], covered_material_ids=[''])
        with self.assertRaisesRegex(ValueError, 'nonempty canonical'):
            delivery_summary([row])

    def test_string_is_not_a_material_id_list(self):
        row = object_row()
        row.update(required_material_ids='wood', covered_material_ids='wood')
        with self.assertRaisesRegex(ValueError, 'explicit list'):
            delivery_summary([row])


def task(mid, depth=1, route='first', **extra):
    return dict(material_id=mid, task_type='OBJECT', attribute_scope='NONE', route_key=route,
                depth=depth, tier=1, family='fixture', eligible=True, **extra)


def scan(pending=None, completed=None):
    return dict(scan_id='scan-1', tree_epoch='tree-old', spent=dict(claims=7, seconds=100, routes=7),
                pending=pending or [], completed=completed or [], leases=[dict(token='old-token')])


class FrontierContracts(unittest.TestCase):
    def test_new_depth_resorts_without_resetting_spend(self):
        old = scan([task('a'), task('b')])
        out = migrate_frontier(old, [task('a', 8), task('b', 1)], 'tree-new')
        self.assertEqual([x['material_id'] for x in out['pending']], ['b', 'a'])
        self.assertEqual(out['spent'], old['spent'])
        self.assertEqual((out['old_tree_epoch'], out['tree_epoch']), ('tree-old', 'tree-new'))

    def test_completed_routes_not_replayed_when_shallower(self):
        old = scan(completed=[task('a', 9)])
        out = migrate_frontier(old, [task('a', 0)], 'tree-new')
        self.assertEqual(out['pending'], [])
        self.assertEqual(out['next_scan'], [])

    def test_alias_merge_preserves_completion_and_spend(self):
        old = scan([task('alias')], [task('canonical')])
        out = migrate_frontier(old, [task('alias')], 'tree-new', {'alias': 'canonical'})
        self.assertEqual(out['pending'], [])
        self.assertEqual(len(out['completed']), 1)
        self.assertEqual(out['spent']['claims'], 7)

    def test_alias_pending_routes_deduplicate(self):
        old = scan([task('a'), task('b')])
        out = migrate_frontier(old, [task('a'), task('b')], 'tree-new', {'a': 'b'})
        self.assertEqual(len(out['pending']), 1)

    def test_new_optional_subject_waits_next_scan(self):
        out = migrate_frontier(scan([task('a')]), [task('a'), task('new')], 'tree-new')
        self.assertEqual([x['material_id'] for x in out['pending']], ['a'])
        self.assertEqual([x['material_id'] for x in out['next_scan']], ['new'])

    def test_new_urgent_gap_can_preempt_without_reset(self):
        current = task('gap', urgent_existing_object_gap=True, preemption_reason='current object lost rho')
        old = scan()
        out = migrate_frontier(old, [current], 'tree-new')
        self.assertEqual(out['pending'][0]['material_id'], 'gap')
        self.assertEqual(out['spent'], old['spent'])

    def test_urgent_reason_is_required(self):
        with self.assertRaisesRegex(ValueError, 'preemption_reason'):
            migrate_frontier(scan(), [task('a', urgent_existing_object_gap=True)], 'new')

    def test_removed_or_demoted_subject_keeps_audit(self):
        old = scan([task('a')])
        current = task('a')
        current.update(eligible=False, reason='state demoted after retraction')
        out = migrate_frontier(old, [current], 'tree-new')
        self.assertEqual(out['pending'], [])
        self.assertTrue(any(x['status'] == 'INELIGIBLE' for x in out['audit']))

    def test_old_leases_are_revoked(self):
        self.assertEqual(migrate_frontier(scan(), [], 'new')['revoked_lease_tokens'], ['old-token'])

    def test_changed_dependency_requires_new_route(self):
        old = scan(completed=[task('a')])
        out = migrate_frontier(old, [task('a', route='recheck:source-retracted')], 'new')
        self.assertEqual(len(out['next_scan']), 1)
        self.assertEqual(out['completed'][0]['route_key'], 'first')

    def test_alias_cycle_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Alias cycle'):
            migrate_frontier(scan(), [task('a')], 'new', {'a': 'b', 'b': 'a'})

    def test_inputs_are_not_modified(self):
        old, candidates = scan([task('a')]), [task('a', 4)]
        before = copy.deepcopy((old, candidates))
        migrate_frontier(old, candidates, 'new')
        self.assertEqual((old, candidates), before)

    def test_distinct_property_routes_do_not_collide(self):
        a, b = task('a'), task('a')
        a.update(task_type='MATERIAL', attribute_scope='E')
        b.update(task_type='MATERIAL', attribute_scope='nu')
        out = migrate_frontier(scan([a, b]), [a, b], 'new')
        self.assertEqual(len(out['pending']), 2)

    def test_completed_E_does_not_skip_nu(self):
        a, b = task('a'), task('a')
        a.update(task_type='MATERIAL', attribute_scope='E')
        b.update(task_type='MATERIAL', attribute_scope='nu')
        out = migrate_frontier(scan([b], [a]), [b], 'new')
        self.assertEqual(len(out['pending']), 1)
        self.assertEqual(out['pending'][0]['attribute_scope'], 'nu')

    def test_missing_attribute_scope_is_rejected(self):
        row = task('a')
        del row['attribute_scope']
        with self.assertRaisesRegex(ValueError, 'attribute_scope'):
            migrate_frontier(scan(), [row], 'new')

    def test_multi_property_scope_order_is_canonical(self):
        a, b = task('a'), task('a')
        a.update(attribute_scope='rho+E')
        b.update(attribute_scope='E+rho')
        out = migrate_frontier(scan([a], [b]), [a], 'new')
        self.assertEqual(out['pending'], [])


if __name__ == '__main__':
    unittest.main()
