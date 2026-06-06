#!/usr/bin/env python3
"""Fail CI when the pytest pass rate is below the required threshold."""

import sys

from junit_summary import parse_junit_xml


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: check_test_pass_rate.py <junit-xml> <min-pass-rate>")
        sys.exit(2)

    report_path = sys.argv[1]
    min_pass_rate = float(sys.argv[2])

    summary = parse_junit_xml(report_path)

    if summary.tests == 0:
        print("No tests were executed.")
        sys.exit(1)

    print(
        f"Passed: {summary.passed}, Failed: {summary.failed}, "
        f"Skipped: {summary.skipped}, Total: {summary.tests}"
    )
    print(f"Pass rate: {summary.pass_rate:.1%} (required: {min_pass_rate:.0%})")

    if summary.pass_rate < min_pass_rate:
        print("CI failed: pass rate is below the required threshold.")
        sys.exit(1)

    print("CI passed: pass rate threshold met.")


if __name__ == "__main__":
    main()
