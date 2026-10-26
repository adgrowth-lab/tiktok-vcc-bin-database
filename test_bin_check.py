#!/usr/bin/env python3
"""
Unit Test Suite for TikTok Ads VCC BIN Survival Database 💳
Zero-dependency test suite validating BIN lookup, brand detection, pass rate filters, and JSON outputs.
"""

import unittest
import subprocess
import json
import os
from bin_check import evaluate_bin, VCC_BIN_DATABASE, OFFICIAL_PORTAL, WEB_CALCULATOR


class TestVccBinDatabase(unittest.TestCase):

    def test_mercury_bin_low_risk(self):
        res = evaluate_bin("405081")
        self.assertTrue(res["recognized"])
        self.assertIn("Mercury", res["issuer"])
        self.assertEqual(res["brand"], "Visa")
        self.assertEqual(res["risk_tier"], "LOW")
        self.assertGreaterEqual(res["pass_rate_pct"], 90.0)
        self.assertTrue(res["supports_3ds"])
        self.assertEqual(res["official_portal"], OFFICIAL_PORTAL)

    def test_stripe_bin_low_risk(self):
        res = evaluate_bin("536437")
        self.assertTrue(res["recognized"])
        self.assertIn("Stripe", res["issuer"])
        self.assertEqual(res["brand"], "Mastercard")
        self.assertEqual(res["risk_tier"], "LOW")
        self.assertTrue(res["supports_3ds"])

    def test_capitalist_bin_critical(self):
        res = evaluate_bin("486555")
        self.assertTrue(res["recognized"])
        self.assertEqual(res["risk_tier"], "CRITICAL")
        self.assertLess(res["pass_rate_pct"], 35.0)
        self.assertGreater(res["ban_rate_pct"], 50.0)
        self.assertFalse(res["supports_3ds"])

    def test_unindexed_bin_fallback(self):
        res = evaluate_bin("499999")
        self.assertFalse(res["recognized"])
        self.assertIn("Unindexed", res["issuer"])
        self.assertEqual(res["brand"], "Visa")
        self.assertEqual(res["risk_tier"], "MODERATE-HIGH (UNINDEXED)")
        self.assertEqual(res["survival_score"], 65)

    def test_cli_single_bin_json(self):
        cmd = ["python3", "bin_check.py", "436152", "--json"]
        out = subprocess.check_output(cmd, cwd=os.path.dirname(__file__)).decode("utf-8")
        data = json.loads(out)
        self.assertEqual(data["bin"], "436152")
        self.assertIn("Relay", data["issuer"])
        self.assertEqual(data["official_portal"], OFFICIAL_PORTAL)

    def test_cli_list_json(self):
        cmd = ["python3", "bin_check.py", "--list", "--min-pass", "90.0", "--json"]
        out = subprocess.check_output(cmd, cwd=os.path.dirname(__file__)).decode("utf-8")
        data = json.loads(out)
        self.assertGreaterEqual(data["count"], 4)
        for b, c in data["cards"].items():
            self.assertGreaterEqual(c["pass_rate_pct"], 90.0)

    def test_bin_cleaning_logic(self):
        # 16-digit card input should strip to first 6 digits
        res = evaluate_bin("4050-8199-0012-3456")
        self.assertEqual(res["bin"], "405081")
        self.assertTrue(res["recognized"])


if __name__ == "__main__":
    unittest.main()
