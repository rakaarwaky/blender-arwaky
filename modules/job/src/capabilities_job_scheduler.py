"""Capability: Background job scheduler implementation (FR-JOB-005).

Provides JobSchedulerCapability for JobSchedulerProtocol contract.
"""

from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import AssetId, ProviderName
from modules.shared.src.job.contract_job_protocol import JobSchedulerProtocol

logger = logging.getLogger("BlenderMCPServer")


class JobSchedulerCapability(JobSchedulerProtocol):
    """Capability for submitting background download jobs."""

    async def submit_download(
        self,
        provider: ProviderName,
        asset_id: AssetId,
        cache_path: str,
    ) -> str:
        """Submit a download task for background execution."""
        logger.info("Submitting download job for %s / %s to %s", provider, asset_id, cache_path)
        return f"job-{provider}-{asset_id}"
