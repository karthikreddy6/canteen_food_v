"""Quick test to verify the email module works end-to-end via app config."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.email import send_email


async def main():
    result = await send_email(
        to="karthikreddy4516@gmail.com",
        subject="OnFood SMTP Test - Zoho Integration Working",
        body=(
            "<h2>OnFood Email Integration</h2>"
            "<p>This is a test email confirming that Zoho SMTP is correctly "
            "configured on the OnFood backend server.</p>"
            "<p><b>Server:</b> smtp.zoho.in:587</p>"
            "<p><b>From:</b> contact@krtech.online</p>"
            "<hr>"
            "<p style='color: #888;'>This is an automated test. No action required.</p>"
        ),
        html=True,
    )
    if result:
        print("SUCCESS: Email sent via app.email module!")
    else:
        print("FAILED: Email sending failed. Check logs.")


asyncio.run(main())
