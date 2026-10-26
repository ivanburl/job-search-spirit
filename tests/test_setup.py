import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/setup.py"
spec = importlib.util.spec_from_file_location("plugin_setup", SCRIPT)
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupTests(unittest.TestCase):
    def test_validated_session_is_ready(self):
        self.assertEqual(setup.classify_session(0, "Session is valid (private path)"), {"status": "ready"})

    def test_unvalidated_zero_exit_is_not_ready(self):
        self.assertEqual(setup.classify_session(0, "Source cookie validity is not verified")["status"], "needs_action")

    def test_failures_continue_independent_checks(self):
        def run(command, **kwargs):
            if "--help" in command:
                raise RuntimeError("PDF dependencies unavailable")
            return 0, "Session is valid"
        with patch.object(setup, "run", side_effect=run):
            result = setup.readiness("uv", install=True)
        self.assertFalse(result["ready"])
        self.assertEqual(result["checks"]["cv"]["status"], "failed")
        self.assertEqual(result["checks"]["linkedin_mcp"]["status"], "ready")

    def test_doctor_does_not_request_browser_installation(self):
        with patch.object(setup, "run", return_value=(0, "Session is valid")) as run:
            result = setup.readiness("uv", install=False)
        self.assertTrue(result["ready"])
        self.assertFalse(any("install" in call.args[0] for call in run.call_args_list))


if __name__ == "__main__":
    unittest.main()
