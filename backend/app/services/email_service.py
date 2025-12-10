import random
import string
from datetime import datetime, timedelta
from typing import Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def generate_otp(length: int = 6) -> str:
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))

async def send_otp_email(email: str, otp: str, username: str) -> bool:
    """Send OTP verification email"""
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Your OTP Code - {settings.PROJECT_NAME}"
        message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM}>"
        message["To"] = email

        # Email body
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #4F46E5;">Welcome to {settings.PROJECT_NAME}!</h2>
              <p>Hi {username},</p>
              <p>Thank you for signing up! Please use the following OTP code to verify your email address:</p>
              <div style="background-color: #F3F4F6; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
                <h1 style="color: #4F46E5; font-size: 36px; margin: 0; letter-spacing: 8px;">{otp}</h1>
              </div>
              <p>This code will expire in 10 minutes.</p>
              <p>If you didn't request this code, please ignore this email.</p>
              <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
              <p style="color: #6B7280; font-size: 12px;">
                This is an automated email from {settings.PROJECT_NAME}. Please do not reply.
              </p>
            </div>
          </body>
        </html>
        """

        text = f"""
        Welcome to {settings.PROJECT_NAME}!
        
        Hi {username},
        
        Thank you for signing up! Please use the following OTP code to verify your email address:
        
        {otp}
        
        This code will expire in 10 minutes.
        
        If you didn't request this code, please ignore this email.
        """

        message.attach(MIMEText(text, "plain"))
        message.attach(MIMEText(html, "html"))

        # Send email
        if not settings.SMTP_USER or not settings.SMTP_HOST:
            print(f"WARNING: SMTP not configured. OTP for {email}: {otp}")
            return True  # Return True in development without SMTP

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        
        print(f"OTP email sent successfully to {email}")
        return True

    except Exception as e:
        print(f"Failed to send OTP email: {str(e)}")
        # In development, print OTP to console
        print(f"DEVELOPMENT OTP for {email}: {otp}")
        return False
