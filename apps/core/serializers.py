from rest_framework import serializers

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Here you would check if a user with this email exists
        # For security reasons, we don't want to reveal if an email is registered or not
        # So we just validate the format. The view will handle the logic.
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        min_length=8
    )

class OTPVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(min_length=6, max_length=6) 