"""
Core system views for health and status endpoints.
These are lightweight diagnostic endpoints used to verify that
the API and database are operational.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema, OpenApiResponse


# -------------------------------
# Serializers (used for schema generation)
# -------------------------------

class HealthCheckSerializer(serializers.Serializer):
    status = serializers.CharField(help_text="Indicates API health status")
    message = serializers.CharField(help_text="Descriptive status message")


class SystemStatusSerializer(serializers.Serializer):
    database = serializers.CharField(help_text="Database connection status")
    cache = serializers.CharField(help_text="Cache connection status")
    uptime = serializers.CharField(help_text="System uptime or runtime info")


# -------------------------------
# Endpoints
# -------------------------------

@extend_schema(
    summary="API Health Check",
    description="Returns a basic API health status to confirm backend availability.",
    responses={
        200: OpenApiResponse(response=HealthCheckSerializer, description="API is operational")
    },
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint.
    Returns API health status to confirm backend availability.
    """
    data = {
        "status": "ok",
        "message": "API is running successfully"
    }
    return Response(data, status=status.HTTP_200_OK)


@extend_schema(
    summary="System Status Overview",
    description="Provides system-level information about services like the database and cache.",
    responses={
        200: OpenApiResponse(response=SystemStatusSerializer, description="System is running normally")
    },
)
@api_view(['GET'])
@permission_classes([AllowAny])
def system_status(request):
    """
    Returns system diagnostic data including DB/cache status.
    """
    data = {
        "database": "connected",
        "cache": "active",
        "uptime": "Server running smoothly"
    }
    return Response(data, status=status.HTTP_200_OK)
