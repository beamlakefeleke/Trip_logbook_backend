from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta

# 🚛 Custom User Model (Driver & Admin)
class User(AbstractUser):
    role = models.CharField(
        max_length=10, 
        choices=[("driver", "Driver"), ("admin", "Admin")], 
        default="driver"
    )

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",  # ✅ Fix conflict
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",  # ✅ Fix conflict
        blank=True
    )

# 🚚 Trip Model (Stores trip details)
class Trip(models.Model):
    STATUS_CHOICES = [
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trips")
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    cycle_used = models.FloatField()  # Hours already used in 70-hour/8-day cycle
    fuel_stops = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ongoing")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def calculate_total_hours(self):
        """Calculate total driving + on-duty hours for compliance"""
        log_entries = self.logs.all()
        total_hours = sum(entry.duration() for entry in log_entries)  # ✅ Fixed function call
        return total_hours

    def calculate_remaining_hours(self):
        """Calculate remaining hours in the 70-hour/8-day rule"""
        return max(70 - self.calculate_total_hours(), 0)

    def __str__(self):
        return f"Trip {self.id} - {self.pickup_location} to {self.dropoff_location} ({self.status})"

# 📋 Log Entry Model (Electronic Logging Device - ELD)
class LogEntry(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="logs")  # ✅ Fixed ForeignKey reference
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="driver_log_entries") 

    time_started = models.DateTimeField()
    time_ended = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("Driving", "Driving"),
            ("On Duty", "On Duty"),
            ("Sleeper Berth", "Sleeper Berth"),
            ("Off Duty", "Off Duty"),
        ],
    )
    location = models.CharField(max_length=255)
    remarks = models.TextField(blank=True, null=True)

    def duration(self):
        """Calculate the duration of this log entry in hours."""
        duration = self.time_ended - self.time_started
        return round(duration.total_seconds() / 3600, 2)  # ✅ Convert seconds to hours

    def __str__(self):
        return f"{self.status} from {self.time_started} to {self.time_ended} ({self.driver.username})"

# 🚀 Function to Auto-Generate Log Sheets
def generate_log_sheet(trip):
    """
    Automatically creates log entries based on trip duration.
    This function simulates 11-hour driving limit and required 10-hour break.
    """
    current_time = datetime.now()
    remaining_hours = trip.calculate_remaining_hours()

    logs = []
    while remaining_hours > 0:
        if remaining_hours >= 11:
            logs.append(LogEntry(
                trip=trip,
                driver=trip.driver,
                time_started=current_time,
                time_ended=current_time + timedelta(hours=11),
                status="Driving",
                location=trip.current_location,
                remarks="Maximum allowed driving time reached."
            ))
            current_time += timedelta(hours=11)
            remaining_hours -= 11

        if remaining_hours > 0:
            logs.append(LogEntry(
                trip=trip,
                driver=trip.driver,
                time_started=current_time,
                time_ended=current_time + timedelta(hours=10),
                status="Sleeper Berth",
                location=trip.current_location,
                remarks="Mandatory rest period."
            ))
            current_time += timedelta(hours=10)
            remaining_hours -= 10

    LogEntry.objects.bulk_create(logs)  # ✅ Ensure all objects are added before bulk_create()
    return logs

# ✅ Truck Model (Optional - Track which truck is assigned to a trip)
class Truck(models.Model):
    plate_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Truck {self.plate_number} ({self.model})"
