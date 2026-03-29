from django.conf import settings
from rest_framework.permissions import BasePermission


class InternalApiTokenPermission(BasePermission):
    message = "Неверный внутренний API-токен."

    def has_permission(self, request, view):
        token = request.headers.get("X-Internal-Api-Key") or request.query_params.get("token")
        return bool(token and token == settings.INTERNAL_API_TOKEN)
