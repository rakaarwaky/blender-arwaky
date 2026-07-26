"""TDD suite for FR-JOB-005 (Background Capacity Enforcement).

Exercises JobCapacityEnforcer in isolation via injected active-count source.

RED → GREEN: targets the committed JobCapacityProtocol + JobCapacityEnforcer.
"""

from __future__ import annotations

import pytest

from modules.job.src.capabilities_job_capacity import CapacityError, JobCapacityEnforcer
from modules.shared.src.common.taxonomy_core_vo import JobId


def _enforcer(max_concurrent: int, active: int) -> JobCapacityEnforcer:
    return JobCapacityEnforcer(max_concurrent=max_concurrent, active_source=lambda: active)


def test_fr_job_005_accepts_when_under_limit():
    e = _enforcer(max_concurrent=3, active=1)
    accepted, current = e.check_capacity(1)
    assert accepted is True
    assert current == 1


def test_fr_job_005_rejects_when_at_limit():
    e = _enforcer(max_concurrent=3, active=3)
    accepted, current = e.check_capacity(1)
    assert accepted is False
    assert current == 3


def test_fr_job_005_reserve_slot_succeeds_under_limit():
    e = _enforcer(max_concurrent=3, active=1)
    assert e.reserve_slot(JobId("job-1")) is True
    # reservation counts as active
    assert e.active_count() == 2


def test_fr_job_005_reserve_slot_rejected_at_limit():
    e = _enforcer(max_concurrent=3, active=3)
    assert e.reserve_slot(JobId("job-x")) is False
    assert e.active_count() == 3


def test_fr_job_005_release_slot_frees_capacity():
    e = _enforcer(max_concurrent=3, active=2)
    e.reserve_slot(JobId("job-1"))
    assert e.active_count() == 3
    e.release_slot(JobId("job-1"))
    assert e.active_count() == 2


def test_fr_job_005_capacity_error_type_exists():
    assert issubclass(CapacityError, Exception)
