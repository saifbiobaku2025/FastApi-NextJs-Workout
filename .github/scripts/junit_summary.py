#!/usr/bin/env python3
"""Parse JUnit XML test reports into summary counts."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class JUnitSummary:
    tests: int
    failures: int
    errors: int
    skipped: int

    @property
    def failed(self) -> int:
        return self.failures + self.errors

    @property
    def passed(self) -> int:
        return self.tests - self.failed - self.skipped

    @property
    def pass_rate(self) -> float:
        if self.tests == 0:
            return 0.0
        return self.passed / self.tests


def parse_junit_xml(report_path: str | Path) -> JUnitSummary:
    root = ET.parse(report_path).getroot()

    if root.tag == "testsuite":
        suites = [root]
    else:
        suites = root.findall("testsuite")

    tests = sum(int(suite.attrib.get("tests", 0)) for suite in suites)
    failures = sum(int(suite.attrib.get("failures", 0)) for suite in suites)
    errors = sum(int(suite.attrib.get("errors", 0)) for suite in suites)
    skipped = sum(int(suite.attrib.get("skipped", 0)) for suite in suites)

    return JUnitSummary(
        tests=tests,
        failures=failures,
        errors=errors,
        skipped=skipped,
    )
