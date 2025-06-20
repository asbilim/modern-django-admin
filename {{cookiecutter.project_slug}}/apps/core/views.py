from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.core.signing import Signer, BadSignature, SignatureExpired
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    TwoFactorEnableSerializer,
    TwoFactorVerifySerializer,
    TwoFactorDisableSerializer,
    TwoFactorTokenVerifySerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)
import time
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import qrcode.image.svg
from io import BytesIO
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Manage the current user's profile data.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.GenericAPIView):
    """
    Change password for the current user.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been updated."}, status=status.HTTP_200_OK)

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            signer = Signer(salt='password-reset')
            timestamp = int(time.time())
            value = f"{user.pk}:{timestamp}"
            token = signer.sign(value)

            # In a real application, you would build a full URL with the domain
            reset_link = f"/password-reset-confirm?token={token}" # Example link
            # Send email
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            # We don't want to reveal if the user exists or not
            pass
        
        return Response(
            {"message": "If an account with that email exists, a password reset link has been sent."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        
        signer = Signer(salt='password-reset')
        try:
            signed_value = signer.unsign(token)
            user_pk, timestamp_str = signed_value.split(':')
            timestamp = int(timestamp_str)

            # Check if token is older than 10 minutes (600 seconds)
            if time.time() - timestamp > 600:
                 raise SignatureExpired("Token has expired.")

            user = User.objects.get(pk=user_pk)
            user.set_password(password)
            user.save()
            
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        
        except (BadSignature, SignatureExpired):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorEnableView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        # Delete any existing devices for this user to ensure a fresh start
        TOTPDevice.objects.filter(user=user).delete()
        
        # Create a new, unconfirmed device
        device = TOTPDevice.objects.create(user=user, name='default', confirmed=False)
        
        # Get QR code
        qr_url = device.config_url
        img = qrcode.make(qr_url, image_factory=qrcode.image.svg.SvgImage)
        
        stream = BytesIO()
        img.save(stream)

        return Response({
            "qr_code": stream.getvalue().decode(),
            "secret_key": device.key
        }, status=status.HTTP_200_OK)


class TwoFactorVerifyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TwoFactorVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "2FA verified and enabled successfully."}, status=status.HTTP_200_OK)


class TwoFactorDisableView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        devices = TOTPDevice.objects.filter(user=user)
        devices.delete()
        return Response({"message": "2FA has been disabled."}, status=status.HTTP_200_OK)


class TwoFactorTokenVerifyView(generics.GenericAPIView):
    """
    Takes username, password, and OTP to verify and return tokens.
    """
    permission_classes = [AllowAny]
    serializer_class = TwoFactorTokenVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }) 