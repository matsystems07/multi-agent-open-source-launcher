from datetime import datetime, timezone
import uuid
from typing import TypedDict, Optional, Any, Dict


class AgentMessage(TypedDict):
    messageid: str
    fromagent: str
    toagent: str
    messagetype: str
    payload: Dict[str, Any]
    timestamp: str
    parentmessageid: Optional[str]


def make_message(
    from_agent: str,
    to_agent: str,
    message_type: str,
    payload: Dict[str, Any],
    parent_message_id: Optional[str] = None
) -> AgentMessage:
    return {
        "messageid": str(uuid.uuid4()),
        "fromagent": from_agent,
        "toagent": to_agent,
        "messagetype": message_type,
        "payload": payload,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parentmessageid": parent_message_id,
    }