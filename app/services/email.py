import asyncio
import os

import resend

resend.api_key = os.getenv("RESEND_API_KEY", "")


async def send_api_key_email(
    email:      str,
    name:       str,
    api_key:    str | None,
    plan:       str,
    is_upgrade: bool = False,
) -> None:
    """Send API key to new tenant or upgrade confirmation."""

    if is_upgrade:
        subject = f"Your MemLayer plan has been upgraded to {plan.title()}"
        body    = _upgrade_email(name, plan)
    else:
        if api_key is None:
            raise ValueError("api_key is required when sending a welcome email")
        subject = "Your MemLayer API Key"
        body    = _welcome_email(name, api_key, plan)

    await asyncio.to_thread(_send_email, email, subject, body)


def _send_email(email: str, subject: str, body: str) -> None:
    resend.Emails.send({
        "from":    "sunvictor567@gmail.com",
        "to":      email,
        "subject": subject,
        "html":    body,
    })


def _welcome_email(name: str, api_key: str, plan: str) -> str:
    return f"""
    <h2>Welcome to MemLayer, {name}!</h2>
    <p>Your API key is ready. Keep it safe — it won't be shown again.</p>

    <code style="
        background:#1a1a1a;
        color:#00d4ff;
        padding:16px;
        display:block;
        border-radius:8px;
        font-size:14px;
        margin:20px 0;
    ">{api_key}</code>

    <h3>Quick Start</h3>
    <pre style="background:#1a1a1a;color:#e2e8f0;padding:16px;border-radius:8px;">
pip install memlayer-py

from memlayer import MemLayerClient

client = MemLayerClient(api_key="{api_key}")
client.remember("User prefers dark mode", user_id="u1", agent_id="bot")
    </pre>

    <p>
        <a href="https://memlayer.online/docs">API Docs</a> ·
        <a href="https://memlayer.online">Dashboard</a> ·
        <a href="mailto:support@memlayer.online">Support</a>
    </p>

    <p>You're on the <strong>{plan.title()}</strong> plan.</p>
    <p>Reply to this email if you need anything.</p>

    <p>— Victor, MemLayer</p>
    """


def _upgrade_email(name: str, plan: str) -> str:
    return f"""
    <h2>Plan upgraded, {name}!</h2>
    <p>Your MemLayer account has been upgraded to <strong>{plan.title()}</strong>.</p>
    <p>Your existing API key works immediately with your new limits.</p>

    <p>
        <a href="https://memlayer.online/docs">API Docs</a> ·
        <a href="mailto:sunvictor567@gmail.com">Support</a>
    </p>

    <p>— Victor, MemLayer</p>
    """