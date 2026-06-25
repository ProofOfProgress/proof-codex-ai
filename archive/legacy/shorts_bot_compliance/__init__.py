"""YouTube YPP / inauthentic-content guards."""

from shorts_bot.compliance.upload_guard import ComplianceReport, check_upload_allowed, record_upload
from shorts_bot.compliance.inauthentic_rules import OPERATING_RULES_BLOCK, risk_signals_for_script

__all__ = [
    "ComplianceReport",
    "check_upload_allowed",
    "record_upload",
    "OPERATING_RULES_BLOCK",
    "risk_signals_for_script",
]
