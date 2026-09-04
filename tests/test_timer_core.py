"""
Unit tests for Core Timer Engine & Power Logic.
"""

import unittest
import os
import sys
import datetime

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.timer import TimerEngine
from core.power import PowerManager

class TestTimerEngine(unittest.TestCase):
    def setUp(self):
        self.engine = TimerEngine()

    def tearDown(self):
        self.engine.cancel()

    def test_calculate_secs_until_future_today(self):
        now = datetime.datetime.now()
        target_hour = (now.hour + 1) % 24
        target_minute = now.minute
        secs = TimerEngine.calculate_secs_until(target_hour, target_minute)
        self.assertGreater(secs, 0)
        self.assertLessEqual(secs, 86400)

    def test_calculate_secs_until_wrap_tomorrow(self):
        now = datetime.datetime.now()
        target_hour = (now.hour - 1) % 24
        target_minute = now.minute
        secs = TimerEngine.calculate_secs_until(target_hour, target_minute)
        self.assertGreater(secs, 20 * 3600)  # Wrapped into tomorrow

    def test_start_countdown_valid(self):
        res = self.engine.start(mode="shutdown", secs=120, trigger_type="countdown")
        self.assertTrue(res["success"])
        state = self.engine.get_state()
        self.assertTrue(state["is_active"])
        self.assertEqual(state["mode"], "shutdown")
        self.assertEqual(state["rem_secs"], 120)
        self.assertEqual(state["total_secs"], 120)

    def test_start_invalid_mode(self):
        res = self.engine.start(mode="invalid_mode", secs=100)
        self.assertFalse(res["success"])

    def test_snooze_updates_both_counters(self):
        self.engine.start(mode="sleep", secs=60)
        res = self.engine.snooze(additional_mins=5)
        self.assertTrue(res["success"])
        state = self.engine.get_state()
        self.assertGreaterEqual(state["rem_secs"], 355)  # 60 + 300 = 360 (allowing 5s buffer)
        self.assertEqual(state["total_secs"], 360)

    def test_cancel_timer(self):
        self.engine.start(mode="lock", secs=100, keep_awake=True)
        self.assertTrue(self.engine.get_state()["is_active"])
        self.assertTrue(self.engine.get_state()["keep_awake"])

        self.engine.cancel()
        state = self.engine.get_state()
        self.assertFalse(state["is_active"])
        self.assertFalse(state["keep_awake"])

if __name__ == "__main__":
    unittest.main()
