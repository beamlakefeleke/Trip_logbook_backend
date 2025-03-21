import requests
from datetime import datetime, timedelta
from django.conf import settings
from .models import LogEntry, Trip
from geopy.distance import geodesic

from api import models

# 📍 API Key for Google Maps / OpenStreetMap (Set in settings.py)
MAPS_API_KEY = getattr(settings, "MAPS_API_KEY", None)


def calculate_distance(pickup, dropoff):
    """
    Calculates the road distance (in miles) between pickup and dropoff using Google Maps API.
    If Google API fails, fall back to geopy (approximate distance).
    """
    if MAPS_API_KEY:
        try:
            url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={pickup}&destinations={dropoff}&key={MAPS_API_KEY}"
            response = requests.get(url).json()
            if response['status'] == 'OK':
                distance = response["rows"][0]["elements"][0]["distance"]["value"] / 1609.34  # Convert meters to miles
                return round(distance, 2)
        except Exception as e:
            print(f"Google Maps API Error: {e}")

    # Fallback: Use geopy (approximate distance)
    try:
        pickup_coords = get_coordinates(pickup)
        dropoff_coords = get_coordinates(dropoff)
        return round(geodesic(pickup_coords, dropoff_coords).miles, 2)
    except Exception as e:
        print(f"Geopy Error: {e}")
        return None


def get_coordinates(location):
    """
    Convert a location (city, state) into latitude/longitude using OpenStreetMap.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
        response = requests.get(url).json()
        if response:
            return float(response[0]["lat"]), float(response[0]["lon"])
    except Exception as e:
        print(f"OpenStreetMap API Error: {e}")
    return None


def generate_log_sheet(trip):
    """
    Automatically generates log entries for a given trip.
    - 11-hour driving limit
    - 10-hour mandatory rest
    - Fueling stops every 1,000 miles (1-hour stops)
    """
    current_time = datetime.now()
    remaining_hours = trip.calculate_remaining_hours()
    distance = calculate_distance(trip.pickup_location, trip.dropoff_location)
    logs = []

    # Estimated time per mile (assuming average 50 mph)
    estimated_travel_time = distance / 50  # in hours

    while remaining_hours > 0 and estimated_travel_time > 0:
        if remaining_hours >= 11 and estimated_travel_time > 11:
            # Driving block (Max 11 hours)
            logs.append(LogEntry(
                trip=trip,
                driver=trip.driver,
                time_started=current_time,
                time_ended=current_time + timedelta(hours=11),
                status="Driving",
                location=trip.current_location,
                remarks="Max driving time reached."
            ))
            current_time += timedelta(hours=11)
            remaining_hours -= 11
            estimated_travel_time -= 11

        # Mandatory 10-hour rest
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

        # Fuel stop every 1,000 miles (1-hour stop)
        if distance > 1000:
            logs.append(LogEntry(
                trip=trip,
                driver=trip.driver,
                time_started=current_time,
                time_ended=current_time + timedelta(hours=1),
                status="On Duty",
                location=trip.current_location,
                remarks="Fueling stop."
            ))
            current_time += timedelta(hours=1)
            remaining_hours -= 1
            distance -= 1000  # Reduce remaining distance

    LogEntry.objects.bulk_create(logs)
    return logs


def check_compliance(driver):
    """
    Checks if a driver is within the 70-hour/8-day rule.
    Returns remaining driving hours.
    """
    last_8_days = datetime.now() - timedelta(days=8)
    total_hours = LogEntry.objects.filter(
        driver=driver,
        time_started__gte=last_8_days
    ).aggregate(total_hours=models.Sum("time_ended") - models.Sum("time_started"))["total_hours"] or 0

    remaining_hours = max(70 - total_hours, 0)
    return {
        "total_hours_last_8_days": total_hours,
        "remaining_hours": remaining_hours,
        "compliance_status": "Allowed to drive" if remaining_hours > 0 else "Out of hours!"
    }
