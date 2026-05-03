from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import boto3

from flare.events import TriggerInfo, TriggerType

if TYPE_CHECKING:
    from mypy_boto3_sns import SNSClient

    from flare.config import FlareConfig


def _trigger_label(trigger: TriggerInfo) -> str:
    """Return a short human-readable label for the trigger source."""
    if trigger.trigger_type == TriggerType.ALARM:
        return f"Alarm: {trigger.alarm_name or 'Unknown'}"
    if trigger.trigger_type == TriggerType.SUBSCRIPTION:
        return "Subscription filter match"
    return "Scheduled scan"


def _format_message(analysis: str, trigger: TriggerInfo) -> str:
    """Build the full notification body with trigger label, timestamp, and RCA."""
    return (
        f"Trigger: {_trigger_label(trigger)}\n"
        f"Time: {datetime.now(tz=UTC).isoformat()}\n\n"
        f"{analysis}"
    )


def notify(
    analysis: str,
    trigger: TriggerInfo,
    config: FlareConfig,
    *,
    sns_client: SNSClient | None = None,
) -> None:
    """Publish the triage analysis to the configured SNS topic.

    The subject line is truncated to 100 characters (SNS limit).
    """
    if sns_client is None:
        sns_client = boto3.client("sns")

    message = _format_message(analysis, trigger)
    subject = f"Flare - {_trigger_label(trigger)}"[:100]

    sns_client.publish(
        TopicArn=config.sns_topic_arn,
        Subject=subject,
        Message=message,
    )
