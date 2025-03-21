from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from .models import Trip, LogEntry, Truck

User = get_user_model()


# 🧑‍✈️ User Serializer (Driver & Admin)
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "password"]
    
    def create(self, validated_data):
        """Create user with hashed password"""
        user = User.objects.create_user(**validated_data)
        return user


# 🚚 Truck Serializer
class TruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Truck
        fields = "__all__"


# 📍 Log Entry Serializer (ELD Compliance)
class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = "__all__"

    def validate(self, data):
        """Ensure log entries comply with ELD rules"""
        driver = data.get("driver")
        time_started = data.get("time_started")
        time_ended = data.get("time_ended")

        if time_started >= time_ended:
            raise serializers.ValidationError("End time must be after start time.")

        # Enforce 11-hour driving rule per day
        daily_logs = LogEntry.objects.filter(
            driver=driver, time_started__date=time_started.date()
        )
        total_hours = sum(
            (log.time_ended - log.time_started).total_seconds() / 3600 for log in daily_logs
        )
        if total_hours + (time_ended - time_started).total_seconds() / 3600 > 11:
            raise serializers.ValidationError("Daily driving limit exceeded (11 hours max).")

        return data


# 🛣️ Trip Serializer (Nested Log Entries)
class TripSerializer(serializers.ModelSerializer):
    driver = UserSerializer(read_only=True)
    truck = TruckSerializer(read_only=True)
    logs = LogEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "driver",
            "truck",
            "pickup_location",
            "dropoff_location",
            "current_location",
            "status",
            "start_time",
            "end_time",
            "logs",
        ]

    def validate(self, data):
        """Ensure trip start time is before end time"""
        if "start_time" in data and "end_time" in data:
            if data["start_time"] >= data["end_time"]:
                raise serializers.ValidationError("Trip end time must be after start time.")

        return data
