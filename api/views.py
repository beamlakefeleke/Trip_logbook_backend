from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import timedelta
from .models import Trip, LogEntry, Truck
from .serializers import TripSerializer, LogEntrySerializer, TruckSerializer, UserSerializer
from .utils import generate_log_sheet  # Function to auto-create log sheets
from .authentication import CustomJWTAuthentication, get_tokens_for_user
from .permissions import IsAdmin, IsOwnerOrAdmin
from django.db.models import Sum
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()


# 🚛 Driver Registration & Authentication
class DriverRegisterView(generics.CreateAPIView):
    """
    Register new drivers.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class DriverLoginView(TokenObtainPairView):
    """
    Driver login to obtain JWT tokens.
    """
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            tokens = get_tokens_for_user(user)
            return Response({"tokens": tokens, "role": user.role})
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class DriverListView(generics.ListAPIView):
    """
    Admin-only endpoint to view all drivers.
    """
    queryset = User.objects.filter(role="driver")
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


# 🚚 Trip ViewSet (CRUD for trips)
class TripViewSet(viewsets.ModelViewSet):
    """
    Manage trips for drivers.
    """
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        """Assign trip to the logged-in driver"""
        serializer.save(driver=self.request.user)

    def get_queryset(self):
        """Allow drivers to see only their trips"""
        if self.request.user.role == "driver":
            return Trip.objects.filter(driver=self.request.user)
        return Trip.objects.all()

    @action(detail=True, methods=['post'])
    def generate_logs(self, request, pk=None):
        """Auto-generate daily log sheets for a trip"""
        trip = self.get_object()
        logs = generate_log_sheet(trip)
        return Response({
            "message": "Logs generated successfully",
            "logs": LogEntrySerializer(logs, many=True).data
        })


# 📋 Log Entry ViewSet (CRUD for ELD logs)
class LogEntryViewSet(viewsets.ModelViewSet):
    """
    Manage electronic log entries for drivers.
    """
    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        """Assign log entry to the trip and driver"""
        trip_id = self.request.data.get("trip")
        trip = Trip.objects.get(id=trip_id)
        serializer.save(driver=self.request.user, trip=trip)

    def get_queryset(self):
        """Drivers can only see their own logs"""
        if self.request.user.role == "driver":
            return LogEntry.objects.filter(driver=self.request.user)
        return LogEntry.objects.all()


# 🚀 Compliance Check (70-hour/8-day Rule)
class ComplianceCheckView(generics.RetrieveAPIView):
    """
    Check if a driver is within legal driving limits (70-hour/8-day rule).
    """
    serializer_class = TripSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        driver = request.user
        last_8_days = now() - timedelta(days=8)
        total_hours = LogEntry.objects.filter(driver=driver, time_started__gte=last_8_days).aggregate(
            total_hours=Sum("time_ended") - Sum("time_started")
        )["total_hours"] or 0

        remaining_hours = max(70 - total_hours, 0)

        return Response({
            "total_hours_last_8_days": total_hours,
            "remaining_hours": remaining_hours,
            "compliance_status": "Allowed to drive" if remaining_hours > 0 else "Out of hours!"
        }, status=status.HTTP_200_OK)


# 🚜 Truck Management
class TruckViewSet(viewsets.ModelViewSet):
    """
    Manage truck details (Admin only).
    """
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
