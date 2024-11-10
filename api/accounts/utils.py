from datetime import timedelta
import random

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import UserOTP


def send_email(subject, message, recipient_list):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=settings.FAIL_SILENTLY,
        )
    except Exception as e:
        print(f"Failed to send email: {e}")


def generate_and_send_otp(user):
    otp = random.randint(100000, 999999)
    user_otp, created = UserOTP.objects.update_or_create(
        user=user,
        defaults={
            "otp": otp,
            "otp_attempts": 3,
            "is_blocked": False,
            "block_time": None,
            "expires_at": timezone.now() + timedelta(minutes=2),
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
        },
    )
    # Save the OTP
    user_otp.save()
    # Send OTP via email
    subject = "OTP Verification"
    message = f"Your OTP is {otp}. It will expire in 2 minutes. Do not share it with anyone."
    send_email(subject, message, [user.email])
    return otp


def send_confirmation_email(request, user, purpose):
    if purpose == "account_confirmation":
        subject = "Account Confirmation"
        message = "Your account confirmed successfully. You can now log in."
        send_email(subject, message, [user.email])
    if purpose == "password_reset":
        subject = "Password Reset Confirmation"
        message = "Your password has been reset successfully. You can now log in with your new password."
        send_email(subject, message, [user.email])
