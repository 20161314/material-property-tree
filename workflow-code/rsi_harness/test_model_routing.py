import unittest

from model_routing import resolve_route


class ModelRoutingTests(unittest.TestCase):
    def test_default_and_critical_tasks_use_sol_high(self):
        for task in ['ordinary', 'source_research', 'taxonomy', 'component_scope', 'code', 'conflict_review', 'merge', 'publish']:
            route = resolve_route(task)
            self.assertEqual((route['model'], route['reasoning_effort']), ('gpt-6.1-sol', 'high'))

    def test_batch_dispatch_uses_luna_max_without_full_history(self):
        route = resolve_route('bulk_review')
        self.assertEqual((route['model'], route['reasoning_effort'], route['fork_turns']), ('gpt-6-luna', 'max', 'none'))
        self.assertFalse(route['dispatch_executed'])

    def test_ambiguous_batch_item_returns_to_sol(self):
        route = resolve_route('bulk_review', escalate=True)
        self.assertEqual((route['model'], route['reasoning_effort']), ('gpt-6.1-sol', 'high'))

    def test_unavailable_requested_model_does_not_silently_fallback(self):
        with self.assertRaises(ValueError):
            resolve_route('bulk_review', available_models=['gpt-6.1-sol'])

    def test_unknown_task_cannot_accidentally_dispatch_a_reviewer(self):
        with self.assertRaises(ValueError):
            resolve_route('bulk_reveiw')


if __name__ == '__main__':
    unittest.main()
