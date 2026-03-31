"""
Two-Factor Authentication utilities for TOTP-based 2FA
"""
import pyotp
import qrcode
from io import BytesIO
import base64
from django_otp.plugins.otp_totp.models import TOTP_DEVICE


def generate_totp_secret():
    """Generate a new TOTP secret"""
    return pyotp.random_base32()


def get_totp_uri(user, secret, issuer='ArtisticSound'):
    """
    Generate TOTP provisioning URI for QR code
    Args:
        user: Django User object
        secret: TOTP secret key
        issuer: Application name to display in authenticator app
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=user.email or user.username,
        issuer_name=issuer
    )


def generate_qr_code(uri):
    """
    Generate QR code image as base64 string
    Args:
        uri: TOTP provisioning URI
    Returns:
        Base64 encoded PNG image string
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"


def verify_totp(user, otp_code):
    """
    Verify TOTP code for user
    Args:
        user: Django User object
        otp_code: 6-digit OTP code to verify
    Returns:
        Boolean indicating if verification was successful
    """
    # Get user's TOTP device
    devices = TOTP_DEVICE.objects.filter(user=user, confirmed=True)
    
    for device in devices:
        if device.verify_token(otp_code):
            return True
    
    return False


def setup_totp_for_user(user, secret):
    """
    Create and return TOTP device for user (not confirmed until verified)
    Args:
        user: Django User object
        secret: TOTP secret key
    Returns:
        TOTP_DEVICE object
    """
    # Delete any existing unconfirmed devices
    TOTP_DEVICE.objects.filter(user=user, confirmed=False).delete()
    
    device = TOTP_DEVICE.objects.create(
        user=user,
        name=f"default",
        key=secret,
        confirmed=False
    )
    return device


def confirm_totp_device(user):
    """Mark TOTP device as confirmed"""
    devices = TOTP_DEVICE.objects.filter(user=user, confirmed=False)
    devices.update(confirmed=True)


def disable_totp(user):
    """Disable 2FA for user"""
    TOTP_DEVICE.objects.filter(user=user, confirmed=True).delete()


def user_has_2fa(user):
    """Check if user has 2FA enabled"""
    return TOTP_DEVICE.objects.filter(user=user, confirmed=True).exists()
