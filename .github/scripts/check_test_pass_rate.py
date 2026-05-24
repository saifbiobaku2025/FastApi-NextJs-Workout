#!/usr/bin/env python3
"""Fail CI when the pytest pass rate is below the required threshold."""

import sys
import xml.etree.ElementTree as ET


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: check_test_pass_rate.py <junit-xml> <min-pass-rate>")
        sys.exit(2)

    report_path = sys.argv[1]
    min_pass_rate = float(sys.argv[2])

    root = ET.parse(report_path).getroot()

    if root.tag == "testsuite":
        suites = [root]
    else:
        suites = root.findall("testsuite")

    tests = sum(int(suite.attrib.get("tests", 0)) for suite in suites)
    failures = sum(int(suite.attrib.get("failures", 0)) for suite in suites)
    errors = sum(int(suite.attrib.get("errors", 0)) for suite in suites)
    skipped = sum(int(suite.attrib.get("skipped", 0)) for suite in suites)

    if tests == 0:
        print("No tests were executed.")
        sys.exit(1)

    failed = failures + errors
    passed = tests - failed - skipped
    pass_rate = passed / tests

    print(f"Passed: {passed}, Failed: {failed}, Skipped: {skipped}, Total: {tests}")
    print(f"Pass rate: {pass_rate:.1%} (required: {min_pass_rate:.0%})")

    if pass_rate < min_pass_rate:
        print("CI failed: pass rate is below the required threshold.")
        sys.exit(1)

    print("CI passed: pass rate threshold met.")


if __name__ == "__main__":
    main()
