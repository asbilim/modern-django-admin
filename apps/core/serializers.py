from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import qrcode.image.svg
from io import BytesIO
import time
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    is_2fa_enabled = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_2fa_enabled')
        read_only_fields = ('email', 'is_2fa_enabled')

    def get_is_2fa_enabled(self, user):
        return TOTPDevice.objects.filter(user=user, confirmed=True).exists()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("No user is associated with this email address."))
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        min_length=8,
        write_only=True
    )

class TwoFactorEnableSerializer(serializers.Serializer):
    """
    Serializer for enabling 2FA. Generates a QR code.
    """
    def to_representation(self, instance):
        user = self.context['request'].user
        # Delete any unconfirmed devices for this user to ensure a fresh start
        TOTPDevice.objects.filter(user=user, confirmed=False).delete()
        
        device, _ = TOTPDevice.objects.get_or_create(user=user, name='default', confirmed=False)
        
        # Generate QR code
        uri = device.config_url
        img = qrcode.make(uri, image_factory=qrcode.image.svg.SvgImage)
        stream = BytesIO()
        img.save(stream)

        return {
            'secret_key': device.key,
            'qr_code': stream.getvalue().decode('utf-8')
        }

class TwoFactorVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying the OTP to confirm 2FA setup.
    """
    otp = serializers.CharField(required=True, min_length=6, max_length=6)

    def validate_otp(self, value):
        user = self.context['request'].user
        device = TOTPDevice.objects.filter(user=user, confirmed=False).first()

        if not device:
            raise serializers.ValidationError(_("No pending 2FA setup found. Please start the setup process again to get a new QR code."))

        # This is the crucial part: we check the token with a tolerance.
        # This allows for a small time drift between the server and your device.
        if not device.verify_token(value):
            raise serializers.ValidationError(
                _("The OTP code is incorrect or has expired. Please ensure your device's time is synchronized with an internet time server (like time.google.com) and try again.")
            )

        device.confirmed = True
        device.save()
        return value

class TwoFactorDisableSerializer(serializers.Serializer):
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    
    def validate(self, attrs):
        password = attrs.get('password')
        user = self.context['request'].user
        if not user.check_password(password):
            raise serializers.ValidationError(_('Incorrect password.'))
        return attrs

class TwoFactorTokenVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying the OTP and user credentials.
    """
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    otp = serializers.CharField(label=_("One-Time Password"), trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        otp = attrs.get('otp')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')

            device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
            
            if not device:
                raise serializers.ValidationError(_('Two-factor authentication is not properly enabled for this account.'), code='authorization')

            if not device.verify_token(otp):
                raise serializers.ValidationError(_('Invalid OTP. Please ensure your device\'s time is synchronized.'), code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs 