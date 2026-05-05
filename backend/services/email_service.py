"""
Email service — sends OTP codes.
In dev (no SMTP credentials): prints the OTP to stdout instead.
In prod: set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD in .env
"""
from __future__ import annotations

import smtplib
import random
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend.core.config import settings


def generate_otp() -> tuple[str, datetime]:
    """Return a 6-digit OTP string and its expiry (10 minutes from now)."""
    code    = f"{random.randint(0, 999999):06d}"
    expires = datetime.utcnow() + timedelta(minutes=10)
    return code, expires


def send_otp(to_email: str, otp: str, username: str) -> bool:
    """
    Send OTP email. Returns True on success.
    Falls back to console print if SMTP is not configured.
    """
    smtp_host = getattr(settings, "smtp_host", "") or ""
    smtp_user = getattr(settings, "smtp_user", "") or ""
    smtp_pass = getattr(settings, "smtp_password", "") or ""
    smtp_port = int(getattr(settings, "smtp_port", 587) or 587)
    from_addr = getattr(settings, "smtp_from", smtp_user) or smtp_user

    html_body = f"""
    <div style="font-family:'Open Sans',sans-serif;max-width:480px;margin:0 auto;padding:32px 24px;background:#fff;border-radius:12px;border:1px solid #E2E8F0">
      <div style="font-family:'Poppins',sans-serif;font-weight:800;font-size:20px;color:#0F172A;margin-bottom:8px">🦉 Skout</div>
      <h2 style="font-family:'Poppins',sans-serif;font-size:18px;color:#0F172A;margin:0 0 16px">Verify your email</h2>
      <p style="font-size:14px;color:#64748B;line-height:1.7;margin:0 0 24px">
        Hi <strong style="color:#0F172A">{username}</strong>, use this code to verify your Skout account.
        It expires in <strong>10 minutes</strong>.
      </p>
      <div style="background:#EFF6FF;border:1px solid #DBEAFE;border-radius:10px;padding:20px;text-align:center;margin-bottom:24px">
        <span style="font-family:'Poppins',sans-serif;font-size:36px;font-weight:900;letter-spacing:12px;color:#2563EB">{otp}</span>
      </div>
      <p style="font-size:12px;color:#94A3B8;margin:0">If you didn't request this, ignore this email.</p>
    </div>
    """

    if not (smtp_host and smtp_user and smtp_pass):
        # Dev fallback — print to console (SMTP not configured)
        print(f"\n{'='*50}")
        print(f"  OTP for {to_email}: {otp}  (expires in 10 min)")
        print(f"{'='*50}\n")
        return False  # False = caller knows email was NOT sent

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{otp} is your Skout verification code"
        msg["From"]    = f"Skout <{from_addr}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_addr, to_email, msg.as_string())
        return True
    except Exception as exc:
        print(f"[email_service] Failed to send OTP: {exc}")
        # Fallback to console so dev flow isn't blocked
        print(f"  OTP for {to_email}: {otp}")
        return False
