from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from rest_framework import status
from django_otp.plugins.otp_totp.models import TOTPDevice

class TwoFactorTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Check if the user has a 2FA device
        user = self.user
        devices = TOTPDevice.objects.filter(user=user)
        
        if devices.exists() and devices.first().confirmed:
            # 2FA is enabled, so don't return tokens yet.
            # Instead, indicate that 2FA is required.
            data['is_2fa_enabled'] = True
            data.pop('refresh')
            data.pop('access')
        else:
            # 2FA is not enabled, proceed as normal.
            data['is_2fa_enabled'] = False
        
        return data

class TwoFactorTokenObtainPairView(TokenObtainPairView):
    """
    A custom token obtain pair view that handles 2FA.
    """
    serializer_class = TwoFactorTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        data = serializer.validated_data

        if data.get('is_2fa_enabled'):
            return Response({'detail': 'OTP required.', 'is_2fa_enabled': True}, status=status.HTTP_200_OK)
        
        return Response(data, status=status.HTTP_200_OK) 