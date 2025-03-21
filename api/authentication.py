from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication to add role-based claims.
    """

    def authenticate(self, request):
        """
        Authenticate user via JWT token and attach role-based claims.
        """
        try:
            authentication_result = super().authenticate(request)
            if authentication_result is None:
                return None  # No token provided

            user, validated_token = authentication_result

            # Attach user role to request
            request.user.role = validated_token.get("role", "driver")  # Default to driver if role is missing

            return user, validated_token
        except AuthenticationFailed:
            raise AuthenticationFailed(_("Invalid or expired token."))


def get_tokens_for_user(user):
    """
    Generate JWT tokens (Access & Refresh) with user role embedded.
    """
    refresh = RefreshToken.for_user(user)

    # Add custom claims
    refresh["role"] = user.role  # Include user role in token

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
