import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import UserOTP


def reset_otp_data(user):
    user_otp = UserOTP.objects.get(user=user)
    user_otp.otp_attempts = 3
    user_otp.is_blocked = False
    user_otp.is_validated = False
    user_otp.save()


def validate_otp(user, otp):
    user_otp = UserOTP.objects.get(user=user)
    if not user_otp:
        raise ValidationError("OTP for this user does not exist.")
    # Unblock the user if the last OTP attempt was more than 15 minutes ago
    if user_otp.updated_at + timedelta(minutes=15) < timezone.now():
        user_otp.is_blocked = False
        user_otp.otp_attempts = 3
        user_otp.save()

    if user_otp.is_blocked:
        raise ValidationError(
            "Your account is blocked due to too many failed OTP attempts. Please try again later."
        )
    if user_otp.is_max_attempts_reached():
        user_otp.is_blocked = True
        user_otp.save()
        raise ValidationError("Maximum OTP attempts reached. Please try again later.")
    if user_otp.is_expired():
        user_otp.otp_attempts -= 1
        user_otp.save()
        raise ValidationError("The OTP has expired. Please request a new one.")
    if user_otp.otp != otp:
        user_otp.otp_attempts -= 1
        user_otp.save()
        raise ValidationError("Invalid OTP.")


def validate_password_data(
    user=None,
    email=None,
    current_password=None,
    new_password=None,
    new_password_confirm=None,
):
    if current_password and user and not user.check_password(current_password):
        raise ValidationError({"current_password": "Current password is not correct."})

    if current_password and new_password == current_password:
        raise ValidationError(
            {"new_password": "New password cannot be the same as the current password."}
        )

    if new_password_confirm and new_password != new_password_confirm:
        raise ValidationError({"password_confirm": "Passwords do not match."})

    if email and new_password == email:
        raise ValidationError(
            {"new_password": "Password should not be the same as email."}
        )

    if len(new_password) < 8:
        raise ValidationError(
            {"new_password": "Password should be at least 8 characters long."}
        )
    if not any(char.isdigit() for char in new_password):
        raise ValidationError(
            {"new_password": "Password should contain at least 1 digit."}
        )
    if not any(char.isalpha() for char in new_password):
        raise ValidationError(
            {"new_password": "Password should contain at least 1 letter."}
        )

    validate_password(new_password)


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


def send_otp_email(user):
    otp = random.randint(100000, 999999)
    user_otp, created = UserOTP.objects.update_or_create(
        user=user,
        defaults={
            "otp": otp,
            "expires_at": timezone.now() + timedelta(minutes=3),
            "updated_at": timezone.now(),
        },
    )
    user_otp.is_validated = False
    user_otp.save()

    subject = "OTP Verification"
    message = (
        f"Your OTP is {otp}. It will expire in 3 minutes. Do not share it with anyone."
    )
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
    if purpose == "password_change":
        subject = "Password Change Confirmation"
        message = "Your password has been changed successfully. You can now log in with your new password."
        send_email(subject, message, [user.email])
