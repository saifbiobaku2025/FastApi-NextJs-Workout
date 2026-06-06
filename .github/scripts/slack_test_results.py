#!/usr/bin/env python3
"""Post CI test results to a Slack incoming webhook."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from junit_summary import parse_junit_xml


def _status_emoji(status: str) -> str:
    return ":white_check_mark:" if status == "success" else ":x:"


def _format_counts(summary) -> str:
    return (
        f"Passed: {summary.passed} | Failed: {summary.failed} | "
        f"Skipped: {summary.skipped} | Total: {summary.tests} "
        f"({summary.pass_rate:.1%})"
    )


def build_payload(
    *,
    suite: str,
    status: str,
    run_url: str,
    ref: str,
    actor: str,
    pr_title: str | None,
    pr_url: str | None,
    junit_xml: str | None,
) -> dict:
    emoji = _status_emoji(status)
    headline = f"{emoji} *{suite}*"

    if pr_title and pr_url:
        headline += f" — <{pr_url}|{pr_title}>"
    elif pr_title:
        headline += f" — {pr_title}"

    lines = [headline, f"Branch: `{ref}`", f"Triggered by: {actor}"]

    if junit_xml:
        report = Path(junit_xml)
        if report.is_file():
            summary = parse_junit_xml(report)
            if summary.tests > 0:
                lines.append(_format_counts(summary))
            else:
                lines.append("No tests were executed.")
        else:
            lines.append(f"Report not found: `{junit_xml}`")
    else:
        lines.append(f"Job status: {status}")

    lines.append(f"<{run_url}|View workflow run>")

    return {
        "text": f"{suite} CI {status} on {ref}",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "\n".join(lines)},
            }
        ],
    }


def post_to_slack(webhook_url: str, payload: dict) -> None:
    request = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        if response.status >= 400:
            raise RuntimeError(f"Slack webhook returned HTTP {response.status}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--status", required=True, choices=("success", "failure"))
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--junit-xml", default="")
    parser.add_argument("--pr-title", default="")
    parser.add_argument("--pr-url", default="")
    args = parser.parse_args()

    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not webhook_url:
        print("SLACK_WEBHOOK_URL is not set; skipping Slack notification.")
        return

    payload = build_payload(
        suite=args.suite,
        status=args.status,
        run_url=args.run_url,
        ref=args.ref,
        actor=args.actor,
        pr_title=args.pr_title or None,
        pr_url=args.pr_url or None,
        junit_xml=args.junit_xml or None,
    )

    try:
        post_to_slack(webhook_url, payload)
    except (urllib.error.URLError, RuntimeError) as exc:
        print(f"Failed to post Slack notification: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Slack notification sent.")


if __name__ == "__main__":
    main()
