from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.signing import Signer
import time
import pyotp
import urllib.parse

class AuthAPITests(APITestCase):
    """
    Tests for the authentication, password reset, and 2FA API endpoints.
    """
    def setUp(self):
        """
        Set up a test user for authentication-required endpoints.
        """
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword123')
        self.password_reset_url = reverse('password_reset_request')
        self.password_reset_confirm_url = reverse('password_reset_confirm')
        self.token_obtain_url = reverse('token_obtain_pair')
        self.two_fa_enable_url = reverse('2fa_enable')
        self.two_fa_verify_url = reverse('2fa_verify')
        self.two_fa_disable_url = reverse('2fa_disable')

    def test_obtain_jwt_token(self):
        """
        Ensure a user can obtain a JWT token with valid credentials.
        """
        response = self.client.post(self.token_obtain_url, {'username': 'testuser', 'password': 'testpassword123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_password_reset_request(self):
        """
        Ensure a password reset request sends an email.
        """
        response = self.client.post(self.password_reset_url, {'email': 'test@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that one email has been sent.
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password Reset Request')

    def test_password_reset_confirm(self):
        """
        Ensure a password can be reset with a valid token.
        """
        signer = Signer(salt='password-reset')
        value = f"{self.user.pk}:{int(time.time())}"
        token = signer.sign(value)
        
        new_password = 'newtestpassword456'
        data = {'token': token, 'password': new_password}
        response = self.client.post(self.password_reset_confirm_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_password_reset_confirm_invalid_token(self):
        """
        Ensure password reset fails with an invalid token.
        """
        data = {'token': 'invalidtoken', 'password': 'newpassword'}
        response = self.client.post(self.password_reset_confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_2fa_enable_and_verify(self):
        """
        Ensure a user can enable and verify 2FA.
        """
        self.client.force_authenticate(user=self.user)
        
        # 1. Enable 2FA and get QR code/secret
        enable_response = self.client.get(self.two_fa_enable_url)
        self.assertEqual(enable_response.status_code, status.HTTP_200_OK)
        self.assertIn('qr_code', enable_response.data)

        # 2. Verify 2FA with a valid OTP
        from django_otp.plugins.otp_totp.models import TOTPDevice
        device = TOTPDevice.objects.get(user=self.user)
        
        # Extract the secret from the config URL
        query = urllib.parse.urlparse(device.config_url).query
        secret = urllib.parse.parse_qs(query)['secret'][0]
        
        totp = pyotp.TOTP(secret)
        otp = totp.now()
        
        verify_response = self.client.post(self.two_fa_verify_url, {'otp': otp}, format='json')
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

        # 3. Check device is confirmed
        device.refresh_from_db()
        self.assertTrue(device.confirmed)

    def test_2fa_disable(self):
        """
        Ensure a user can disable 2FA.
        """
        # First, enable and verify 2FA
        self.test_2fa_enable_and_verify()

        # Now, disable it
        self.client.force_authenticate(user=self.user)
        disable_response = self.client.post(self.two_fa_disable_url)
        self.assertEqual(disable_response.status_code, status.HTTP_200_OK)

        # Check that the device has been deleted
        from django_otp.plugins.otp_totp.models import TOTPDevice
        self.assertFalse(TOTPDevice.objects.filter(user=self.user).exists()) 