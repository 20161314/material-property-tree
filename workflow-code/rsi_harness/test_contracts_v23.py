"""Behavioral regression tests for RSI 2.3 local design contracts."""
import copy
import unittest

from contracts_v23 import coverage_counts, extend_scan_budget, object_task_eligible, scan_execution_status


def material(key, covered, objects, **changes):
    row = dict(material_id=key, active=True, is_liquid=False, kind='MATERIAL',
               property_covered=covered, has_object=objects)
    return dict(row, **changes)


def scan():
    return dict(scan_id='S1', budget_revision=0, limits=dict(claims=10, seconds=60),
                spent=dict(claims=10, seconds=40), pending=['nu-route'],
                completed=['E-route'], budget_events=[])


def event():
    return dict(scan_id='S1', event_id='B1', expected_revision=0, actor='coordinator',
                reason='Continue unfinished frontier', authorization_scope='User-authorized research',
                created_at='2026-11-14T14:00:00Z', data_epoch='D1', tree_epoch='T1', unfinished_count=1,
                new_limits=dict(claims=20, seconds=120))


class CoverageTests(unittest.TestCase):
    def test_optional_nodes_do_not_change_main_denominator(self):
        rows = [material('used', True, True), material('gap', False, True)]
        before = coverage_counts(rows)
        after = coverage_counts(rows + [material('optional', False, False)])
        self.assertEqual(before['K_object'], after['K_object'])
        self.assertEqual(after['K_object']['ratio'], 0.5)
        self.assertEqual(after['K_all']['ratio'], 1 / 3)

    def test_four_states_and_inactive_scope(self):
        rows = [material(str(i), p, o) for i, (p, o) in enumerate([(True, True), (True, False), (False, True), (False, False)])]
        rows += [material('liquid', False, True, is_liquid=True),
                 material('category', True, True, kind='CATEGORY'),
                 material('special', False, True, kind='SPECIAL'),
                 material('old', False, True, active=False)]
        result = coverage_counts(rows)
        self.assertEqual(result['states'], {1: 1, 2: 1, 3: 1, 4: 1})
        self.assertEqual(result['K_object']['required'], 2)
        self.assertEqual(result['K_all']['required'], 4)

    def test_empty_denominator_is_not_complete(self):
        result = coverage_counts([])
        self.assertIsNone(result['K_object']['ratio'])
        self.assertIsNone(result['K_all']['ratio'])
        self.assertFalse(result['all_required_material_obligations_satisfied'])

    def test_unknown_obligation_blocks_complete_claim(self):
        result = coverage_counts([material('used', True, True)], unresolved_obligations=1)
        self.assertEqual(result['K_object']['ratio'], 1)
        self.assertFalse(result['all_required_material_obligations_satisfied'])

    def test_duplicate_or_unknown_facts_rejected(self):
        row = material('one', True, True)
        with self.assertRaises(ValueError):
            coverage_counts([row, row])
        with self.assertRaises(ValueError):
            coverage_counts([dict(row, is_liquid=None)])


class EligibilityTests(unittest.TestCase):
    def test_discovery_limited_to_covered_states(self):
        self.assertEqual([object_task_eligible('OBJECT_DISCOVERY', state) for state in (1, 2, 3, 4, None)],
                         [True, True, False, False, False])

    def test_all_existing_repairs_allowed_without_coverage(self):
        for task in ('OBJECT_COMPONENT_REPAIR', 'OBJECT_SCOPE_REPAIR', 'OBJECT_ASSET_REPAIR', 'OBJECT_LABEL_REPAIR'):
            for state in (3, None):
                self.assertTrue(object_task_eligible(task, state, True, 'O1', 'OB1'))

    def test_repairs_cannot_admit_new_object(self):
        self.assertFalse(object_task_eligible('OBJECT_COMPONENT_REPAIR', 1, False, 'new', 'x'))
        with self.assertRaises(ValueError):
            object_task_eligible('OBJECT_LABEL_REPAIR', None, True, 'old', '')
        with self.assertRaises(ValueError):
            object_task_eligible('INVENTED_TASK', 1)


class BudgetTests(unittest.TestCase):
    def test_new_run_cannot_reset_exhausted_scan(self):
        current = scan()
        self.assertEqual(scan_execution_status(current, 1, False), 'PAUSED_BUDGET')
        self.assertEqual(scan_execution_status(current, 1, True), 'PAUSED_BUDGET')

    def test_other_budget_axis_and_zero_frontier(self):
        current = scan()
        current['spent'] = dict(claims=1, seconds=60)
        self.assertEqual(scan_execution_status(current, 1), 'PAUSED_BUDGET')
        self.assertEqual(scan_execution_status(current, 0), 'COMPLETE')

    def test_extension_preserves_frontier_spend_history_and_input(self):
        current = scan()
        original = copy.deepcopy(current)
        new = extend_scan_budget(current, event())
        self.assertEqual(current, original)
        for field in ('pending', 'completed', 'spent'):
            self.assertEqual(new[field], current[field])
        self.assertEqual(new['budget_revision'], 1)
        self.assertEqual(len(new['budget_events']), 1)
        self.assertEqual(scan_execution_status(new, 1), 'READY_FOR_NEXT_RUN')
        self.assertEqual(scan_execution_status(new, 1, True), 'RUNNING')

    def test_exact_replay_zero_delta_changed_event_rejected(self):
        new = extend_scan_budget(scan(), event())
        self.assertEqual(extend_scan_budget(new, event()), new)
        changed = dict(event(), reason='Changed')
        with self.assertRaises(ValueError):
            extend_scan_budget(new, changed)

    def test_stale_revision_wrong_scan_rejected(self):
        with self.assertRaises(ValueError):
            extend_scan_budget(scan(), dict(event(), expected_revision=1))
        with self.assertRaises(ValueError):
            extend_scan_budget(scan(), dict(event(), scan_id='other'))
        with self.assertRaises(ValueError):
            extend_scan_budget(scan(), dict(event(), unfinished_count=0))

    def test_no_decrease_no_noop_and_hard_limits(self):
        for limits in (dict(claims=9, seconds=120), dict(claims=10, seconds=60)):
            with self.assertRaises(ValueError):
                extend_scan_budget(scan(), dict(event(), new_limits=limits))
        with self.assertRaises(ValueError):
            extend_scan_budget(scan(), event(), hard_limits=dict(claims=15, seconds=120))

    def test_budget_types_are_explicit_and_finite(self):
        for limits in (dict(claims=True, seconds=120), dict(claims=20, seconds=float('inf')),
                       dict(claims=20, seconds=-1)):
            with self.assertRaises(ValueError):
                extend_scan_budget(scan(), dict(event(), new_limits=limits))


if __name__ == '__main__':
    unittest.main()
