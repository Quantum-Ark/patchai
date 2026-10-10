"""Automated pytest wrapper for the 3 reproducible benchmark cases."""

import pytest
from pathlib import Path
from benchmarks.run_benchmarks import (
    run_benchmark_case_1,
    run_benchmark_case_2,
    run_benchmark_case_3,
)


def test_benchmark_case_1_logic_bug():
    res = run_benchmark_case_1()
    report = res["report"]
    assert report.success is True
    assert len(report.attempts) == 1
    assert report.verification.all_tests_passed is True


def test_benchmark_case_2_boundary_bug():
    res = run_benchmark_case_2()
    report = res["report"]
    assert report.success is True
    assert len(report.attempts) == 1
    assert report.verification.all_tests_passed is True


def test_benchmark_case_3_regression_recovery():
    res = run_benchmark_case_3()
    report = res["report"]
    assert report.success is True
    # Demonstrates multi-attempt recovery: Attempt 1 broke regression, Attempt 2 fixed it
    assert len(report.attempts) == 2
    assert report.attempts[0].test_result.passed is False
    assert report.attempts[1].test_result.passed is True
    assert report.verification.all_tests_passed is True
