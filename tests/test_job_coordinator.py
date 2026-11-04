"""Contract tests for cancellation, stale responses and cloud routing."""
import unittest

from job_coordinator import JobCoordinator, JobState


class JobCoordinatorTests(unittest.TestCase):
    def test_new_job_invalidates_previous_result(self):
        coordinator = JobCoordinator()
        first = coordinator.start("ollama")
        second = coordinator.start("ollama")
        self.assertNotEqual(first.job_id, second.job_id)
        self.assertFalse(coordinator.accept_result(first.job_id))
        self.assertFalse(coordinator.finish(first.job_id))
        self.assertTrue(coordinator.accept_result(second.job_id))

    def test_cloud_requires_explicit_permission(self):
        coordinator = JobCoordinator()
        with self.assertRaises(PermissionError):
            coordinator.start("gemini")
        self.assertIsNone(coordinator.current)
        cloud = coordinator.start("gemini", cloud_allowed=True)
        self.assertEqual(cloud.provider, "gemini")

    def test_cancel_rejects_late_response(self):
        coordinator = JobCoordinator()
        job = coordinator.start("ollama")
        self.assertFalse(coordinator.cancel("other"))
        self.assertTrue(coordinator.cancel(job.job_id))
        self.assertEqual(coordinator.current.state, JobState.CANCELLED)
        self.assertFalse(coordinator.accept_result(job.job_id))
        self.assertFalse(coordinator.finish(job.job_id))
        self.assertFalse(coordinator.cancel(job.job_id))

    def test_completed_job_cannot_complete_twice(self):
        coordinator = JobCoordinator()
        job = coordinator.start("ollama")
        self.assertTrue(coordinator.finish(job.job_id))
        self.assertEqual(coordinator.current.state, JobState.COMPLETED)
        self.assertFalse(coordinator.finish(job.job_id))
        self.assertFalse(coordinator.accept_result(job.job_id))

    def test_failure_is_terminal(self):
        coordinator = JobCoordinator()
        job = coordinator.start("ollama")
        self.assertTrue(coordinator.finish(job.job_id, failed=True))
        self.assertEqual(coordinator.current.state, JobState.FAILED)
        self.assertFalse(coordinator.accept_result(job.job_id))

    def test_invalid_provider_does_not_cancel_current(self):
        coordinator = JobCoordinator()
        job = coordinator.start("ollama")
        with self.assertRaises(ValueError):
            coordinator.start("unknown")
        self.assertTrue(coordinator.accept_result(job.job_id))


if __name__ == "__main__":
    unittest.main()
