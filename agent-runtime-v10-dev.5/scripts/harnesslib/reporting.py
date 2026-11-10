from __future__ import annotations

import sys


class CheckReport:
    """Tri-state check report: failures outrank incomplete evidence."""

    def __init__(self, label: str) -> None:
        self.label = label
        self.passes: list[str] = []
        self.failures: list[str] = []
        self.incomplete: list[str] = []
        self.not_applicable: list[str] = []

    def passed(self, message: str) -> None:
        self.passes.append(message)

    def failed(self, message: str) -> None:
        self.failures.append(message)

    def gap(self, message: str) -> None:
        self.incomplete.append(message)

    def na(self, message: str) -> None:
        self.not_applicable.append(message)

    def emit(self) -> int:
        for message in self.passes:
            print(f"PASS {message}")
        for message in self.not_applicable:
            print(f"NOT_APPLICABLE {message}")
        for message in self.incomplete:
            print(f"INCOMPLETE {message}", file=sys.stderr)
        for message in self.failures:
            print(f"FAIL {message}", file=sys.stderr)
        print(
            f"SUMMARY {self.label} pass={len(self.passes)} "
            f"not_applicable={len(self.not_applicable)} "
            f"incomplete={len(self.incomplete)} fail={len(self.failures)}"
        )
        if self.failures:
            return 1
        if self.incomplete:
            return 3
        return 0
