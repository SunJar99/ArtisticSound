#Goofy ahh authentication module for this project... :)
import pyotp
import qrcode
from io import BytesIO
import base64
from django_otp.plugins.otp_totp.models import TOTP_DEVICE


def generate_totp_secret():
    return pyotp.random_base32()


def get_totp_uri(user, secret, issuer='ArtisticSound'):
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=user.email or user.username,
        issuer_name=issuer
    )


def generate_qr_code(uri):
    
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

    devices = TOTP_DEVICE.objects.filter(user=user, confirmed=True)
    
    for device in devices:
        if device.verify_token(otp_code):
            return True
    
    return False


def setup_totp_for_user(user, secret):

    TOTP_DEVICE.objects.filter(user=user, confirmed=False).delete()
    
    device = TOTP_DEVICE.objects.create(
        user=user,
        name=f"default",
        key=secret,
        confirmed=False
    )
    return device


def confirm_totp_device(user):
    devices = TOTP_DEVICE.objects.filter(user=user, confirmed=False)
    devices.update(confirmed=True)


def disable_totp(user):
    TOTP_DEVICE.objects.filter(user=user, confirmed=True).delete()


def user_has_2fa(user):
    return TOTP_DEVICE.objects.filter(user=user, confirmed=True).exists()
