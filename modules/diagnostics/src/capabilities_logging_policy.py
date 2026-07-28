# Temporary stub - FR-DIA-004 implementation pending
import logging

from modules.shared.src.diagnostics.contract_logging_policy_protocol import LoggingPolicyProtocol


class LoggingPolicyExecutor(LoggingPolicyProtocol):
    def __init__(self):
        pass

    def emit_log(self, level, source, message, **fields):
        logging.getLogger(source).log(level, message)
