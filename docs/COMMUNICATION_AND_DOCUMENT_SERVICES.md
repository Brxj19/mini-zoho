## Communication And Document Services

### Development Mail UI

The Docker Compose stack now includes Mailpit for local email capture.

- SMTP host: `mailpit`
- SMTP port: `1025`
- Web UI: `http://localhost:8025`

No real email is sent in development. Outgoing messages are captured by Mailpit and also recorded in the `email_outbox` table.

### Development SMS Outbox

Development SMS messages are written to the `sms_outbox` table through the local outbox provider.

Super admins can inspect development outboxes through:

- `GET /api/dev/sms-outbox`
- `GET /api/dev/email-outbox`

These endpoints only work when `ENV=development`.

### OTP Verification

Available auth endpoints:

- `POST /api/auth/request-email-verification`
- `POST /api/auth/verify-email`
- `POST /api/auth/request-phone-verification`
- `POST /api/auth/verify-phone`

In development:

- OTP values are stored in `otp_challenges.dev_plaintext_code`
- email OTPs are visible in Mailpit and `email_outbox`
- SMS OTPs are visible in `sms_outbox`

In production:

- raw OTPs are not stored
- only hashed OTP values are persisted

### PDF Documents

Available document endpoints:

- `GET /api/invoices/{invoice_id}/pdf`
- `POST /api/invoices/{invoice_id}/email`
- `GET /api/bills/{bill_id}/pdf`
- `POST /api/bills/{bill_id}/email`

PDFs are rendered from Jinja templates using WeasyPrint with an A4 layout.

### Environment Variables

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `SMTP_FROM_NAME`
- `EMAIL_ENABLED`
- `SMS_PROVIDER`
- `OTP_TTL_MINUTES`
- `OTP_MAX_ATTEMPTS`

### Notes

- Development uses the local SMS outbox provider by default.
- A Twilio placeholder provider exists but is not enabled by default.
- Email sending remains non-production-safe in local development because it targets Mailpit only.
