from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from email.message import EmailMessage
from pathlib import Path

from aiosmtplib import SMTP
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.email_outbox import EmailOutbox

settings = get_settings()
TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates" / "emails"


@dataclass(slots=True)
class EmailAttachment:
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"


class EmailService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.environment = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def send_email(
        self,
        *,
        to: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
        attachments: list[EmailAttachment] | None = None,
        tenant_id: int | None = None,
        user_id: int | None = None,
    ) -> EmailOutbox:
        outbox = EmailOutbox(
            tenant_id=tenant_id,
            user_id=user_id,
            to_email=to,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            provider="smtp",
            status="QUEUED",
        )
        self.db.add(outbox)
        self.db.flush()

        if not settings.email_enabled:
            outbox.status = "DISABLED"
            self.db.add(outbox)
            self.db.flush()
            return outbox

        message = EmailMessage()
        message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        message["To"] = to
        message["Subject"] = subject
        message.set_content(text_body or "Please view this message in an HTML-compatible email client.")
        message.add_alternative(html_body, subtype="html")

        for attachment in attachments or []:
            maintype, subtype = attachment.content_type.split("/", 1)
            message.add_attachment(
                attachment.content,
                maintype=maintype,
                subtype=subtype,
                filename=attachment.filename,
            )

        try:
            asyncio.run(self._send_message(message))
            outbox.status = "SENT"
            outbox.sent_at = datetime.now(UTC)
            outbox.error_message = None
        except Exception as exc:
            outbox.status = "FAILED"
            outbox.error_message = str(exc)
            self.db.add(outbox)
            self.db.flush()
            raise

        self.db.add(outbox)
        self.db.flush()
        return outbox

    def send_template_email(
        self,
        *,
        template_name: str,
        context: dict,
        to: str,
        subject: str,
        attachments: list[EmailAttachment] | None = None,
        tenant_id: int | None = None,
        user_id: int | None = None,
    ) -> EmailOutbox:
        html_template = self.environment.get_template(f"{template_name}.html")
        html_body = html_template.render(**context)

        text_body = None
        text_path = TEMPLATE_DIR / f"{template_name}.txt"
        if text_path.exists():
            text_body = self.environment.get_template(f"{template_name}.txt").render(**context)

        return self.send_email(
            to=to,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            attachments=attachments,
            tenant_id=tenant_id,
            user_id=user_id,
        )

    async def _send_message(self, message: EmailMessage) -> None:
        smtp = SMTP(
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username or None,
            password=settings.smtp_password or None,
            use_tls=False,
            start_tls=False,
        )
        await smtp.connect()
        try:
            await smtp.send_message(message)
        finally:
            await smtp.quit()
