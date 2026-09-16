"""Advanced Calculator in Python.

Includes:
1. Basic & Extended Arithmetic (Add, Subtract, Multiply, Divide, Power, Square Root)
2. Julian Day Calculation (Gregorian Date/Time -> Julian Day)
3. Qibla (Kiblat) Direction Calculation (Latitude/Longitude -> Qibla Bearing from North)
"""

import math
from datetime import datetime


# --- Basic Arithmetic Functions ---

def add(x: float, y: float) -> float:
    return x + y


def subtract(x: float, y: float) -> float:
    return x - y


def multiply(x: float, y: float) -> float:
    return x * y


def divide(x: float, y: float) -> float:
    if y == 0:
        raise ValueError("Cannot divide by zero.")
    return x / y


def power(x: float, y: float) -> float:
    return math.pow(x, y)


def square_root(x: float) -> float:
    if x < 0:
        raise ValueError("Cannot calculate square root of a negative number.")
    return math.sqrt(x)


# --- 1. Julian Day Calculator ---

def calculate_julian_day(year: int, month: int, day: float, hour: int = 12, minute: int = 0, second: int = 0, utc_offset_hours: float = 0.0) -> float:
    """Calculates the Julian Day (JD) from a Gregorian calendar date and time.
    
    Args:
        year: Year (e.g. 2026)
        month: Month (1-12)
        day: Day of month (1-31)
        hour: Hour (0-23), default 12
        minute: Minute (0-59), default 0
        second: Second (0-59), default 0
        utc_offset_hours: Timezone offset in hours relative to UTC (e.g. +7 for WIB)
        
    Returns:
        Julian Day (float)
    """
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12.")
    if day < 1 or day > 31:
        raise ValueError("Day must be between 1 and 31.")

    # Convert time to fractional day in UTC
    time_in_utc_hours = hour + (minute / 60.0) + (second / 3600.0) - utc_offset_hours
    fractional_day = day + (time_in_utc_hours / 24.0)

    y = year
    m = month
    if m <= 2:
        y -= 1
        m += 12

    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4)

    julian_day = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + fractional_day + b - 1524.5
    return julian_day


# --- 2. Qibla (Kiblat) Direction Calculator ---

# Coordinates of the Kaaba in Mecca, Saudi Arabia
MECCA_LAT = 21.422487   # degrees North
MECCA_LON = 39.826206   # degrees East


def calculate_qibla(latitude: float, longitude: float) -> dict:
    """Calculates the Qibla (Kiblat) direction in degrees clockwise from True North.
    
    Args:
        latitude: Latitude of location in degrees (-90.0 to 90.0)
        longitude: Longitude of location in degrees (-180.0 to 180.0)
        
    Returns:
        dict containing bearing in degrees, compass direction description, and distance to Mecca in km.
    """
    if not (-90.0 <= latitude <= 90.0):
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    if not (-180.0 <= longitude <= 180.0):
        raise ValueError("Longitude must be between -180 and 180 degrees.")

    # Convert degrees to radians
    phi_user = math.radians(latitude)
    lambda_user = math.radians(longitude)
    phi_mecca = math.radians(MECCA_LAT)
    lambda_mecca = math.radians(MECCA_LON)

    delta_lambda = lambda_mecca - lambda_user

    # Great circle initial bearing formula to Mecca
    y = math.sin(delta_lambda)
    x = math.cos(phi_user) * math.tan(phi_mecca) - math.sin(phi_user) * math.cos(delta_lambda)

    bearing_rad = math.atan2(y, x)
    bearing_deg = (math.degrees(bearing_rad) + 360.0) % 360.0

    # Great circle distance calculation (Haversine formula)
    dphi = phi_mecca - phi_user
    dlambda = delta_lambda
    haversine_a = math.sin(dphi / 2)**2 + math.cos(phi_user) * math.cos(phi_mecca) * math.sin(dlambda / 2)**2
    distance_km = 6371.0 * 2 * math.atan2(math.sqrt(haversine_a), math.sqrt(1 - haversine_a))

    # Cardinal direction mapping
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    dir_idx = int((bearing_deg + 11.25) / 22.5) % 16
    compass_dir = directions[dir_idx]

    return {
        "bearing_deg": round(bearing_deg, 4),
        "compass_direction": compass_dir,
        "distance_km": round(distance_km, 2)
    }


# --- Interactive CLI Menu ---

def main():
    while True:
        print("\n" + "=" * 48)
        print("          ADVANCED PYTHON CALCULATOR          ")
        print("=" * 48)
        print("1. Addition (+)")
        print("2. Subtraction (-)")
        print("3. Multiplication (*)")
        print("4. Division (/)")
        print("5. Power (x^y)")
        print("6. Square Root (√x)")
        print("7. Julian Day Calculator (Calendar Date)")
        print("8. Qibla (Kiblat) Direction Calculator")
        print("9. Exit")
        print("=" * 48)

        choice = input("Select an option (1-9): ").strip()

        if choice == "9":
            print("\nThank you for using Advanced Calculator. Goodbye!")
            break

        try:
            if choice in ("1", "2", "3", "4", "5"):
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))

                if choice == "1":
                    res = add(num1, num2)
                    print(f"\nResult: {num1} + {num2} = {res}")
                elif choice == "2":
                    res = subtract(num1, num2)
                    print(f"\nResult: {num1} - {num2} = {res}")
                elif choice == "3":
                    res = multiply(num1, num2)
                    print(f"\nResult: {num1} * {num2} = {res}")
                elif choice == "4":
                    res = divide(num1, num2)
                    print(f"\nResult: {num1} / {num2} = {res}")
                elif choice == "5":
                    res = power(num1, num2)
                    print(f"\nResult: {num1} ^ {num2} = {res}")

            elif choice == "6":
                num = float(input("Enter number: "))
                res = square_root(num)
                print(f"\nResult: √{num} = {res}")

            elif choice == "7":
                print("\n--- Julian Day Calculator ---")
                print("Leave blank for current local date & time.")
                date_str = input("Enter date (YYYY-MM-DD) [or press Enter for today]: ").strip()

                if not date_str:
                    now = datetime.now()
                    year, month, day = now.year, now.month, now.day
                    hour, minute, second = now.hour, now.minute, now.second
                else:
                    parts = [int(p) for p in date_str.split("-")]
                    year, month, day = parts[0], parts[1], parts[2]
                    time_str = input("Enter time (HH:MM:SS) [default 12:00:00]: ").strip()
                    if time_str:
                        t_parts = [int(p) for p in time_str.split(":")]
                        hour = t_parts[0]
                        minute = t_parts[1] if len(t_parts) > 1 else 0
                        second = t_parts[2] if len(t_parts) > 2 else 0
                    else:
                        hour, minute, second = 12, 0, 0

                tz_str = input("Enter UTC offset in hours (e.g. +7 for WIB, -5 for EST) [default 0]: ").strip()
                utc_offset = float(tz_str) if tz_str else 0.0

                jd = calculate_julian_day(year, month, day, hour, minute, second, utc_offset)
                print(f"\nJulian Day (JD) for {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d} (UTC{'+' if utc_offset>=0 else ''}{utc_offset}):")
                print(f"-> JD = {jd:.6f}")
                print(f"-> Modified Julian Day (MJD = JD - 2400000.5) = {jd - 2400000.5:.6f}")

            elif choice == "8":
                print("\n--- Qibla (Kiblat) Direction Calculator ---")
                lat = float(input("Enter Latitude (-90 to 90, e.g., -6.2088 for Jakarta or 40.7128 for NYC): "))
                lon = float(input("Enter Longitude (-180 to 180, e.g., 106.8456 for Jakarta or -74.0060 for NYC): "))

                qibla_info = calculate_qibla(lat, lon)
                print(f"\nQibla Direction Results for Lat: {lat}°, Lon: {lon}°:")
                print(f"-> Bearing: {qibla_info['bearing_deg']}° from True North ({qibla_info['compass_direction']})")
                print(f"-> Great Circle Distance to Kaaba (Mecca): {qibla_info['distance_km']} km")

            else:
                print("Invalid choice. Please select an option between 1 and 9.")

        except ValueError as err:
            print(f"\nError: {err}")
        except Exception as err:
            print(f"\nAn unexpected error occurred: {err}")


if __name__ == "__main__":
    import sys
    if "--cli" in sys.argv:
        main()
    else:
        try:
            from app import AdvancedCalculatorApp
            app = AdvancedCalculatorApp()
            app.mainloop()
        except ImportError:
            main()

