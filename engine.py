"""Pure calculator, civil-calendar and approximate solar-time engines.

Numeric contract: finite IEEE-754 doubles, truncating remainder, Gregorian
proleptic dates, and the 30-year arithmetic Islamic calendar (civil epoch).
"""
import json
import math
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DATA = json.loads(Path(__file__).with_name("data.json").read_text(encoding="utf-8"))
MECCA_LAT, MECCA_LON = DATA["MECCA_LAT"], DATA["MECCA_LON"]
HIJRI_MONTHS, HIJRI_MONTHS_SHORT = DATA["HIJRI_MONTHS"], DATA["HIJRI_MONTHS_SHORT"]
GREG_MONTHS, DAYS_ID, CITIES = DATA["GREG_MONTHS"], DATA["DAYS_ID"], DATA["cities"]
PRAYERS = [("imsak", "Imsak"), ("fajr", "Subuh"), ("sunrise", "Terbit"), ("dhuhr", "Dzuhur"), ("asr", "Ashar"), ("maghrib", "Maghrib"), ("isha", "Isya")]
EPOCH = 1948439.5
TOKEN = re.compile(r"\s*(?:(\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)|([A-Za-z]+)|((?:\*\*)|[()+*/%\-]))")


def finite(value):
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Hasil di luar rentang angka.")
    return float(value)


def safe_power(base, exponent):
    if abs(exponent) > 10000:
        raise ValueError("Eksponen terlalu besar (maksimum 10000).")
    try:
        return finite(math.pow(base, exponent))
    except (ValueError, OverflowError) as error:
        raise ValueError("Pangkat di luar domain atau rentang angka.") from error


def evaluate_scientific_expression(expression, degrees=True, answer=0, angle_mode=None):
    if not expression.strip() or len(expression) > 256:
        raise ValueError("Masukkan ekspresi sepanjang 1–256 karakter.")
    mode = angle_mode or ("DEG" if degrees else "RAD")
    if mode not in ("DEG", "RAD", "GRAD"):
        raise ValueError("Mode sudut tidak valid.")
    factor = {"DEG": math.pi / 180, "RAD": 1, "GRAD": math.pi / 200}[mode]
    def tangent(x):
        if abs(math.cos(x * factor)) < 1e-12:
            raise ValueError("Tangen tidak terdefinisi pada sudut ini.")
        return math.tan(x * factor)
    def factorial(x):
        if not x.is_integer() or not 0 <= x <= 170:
            raise ValueError("Faktorial membutuhkan bilangan bulat 0–170.")
        result = 1.0
        for i in range(2, int(x) + 1):
            result *= i
        return result
    functions = {"sin": lambda x: math.sin(x * factor), "cos": lambda x: math.cos(x * factor), "tan": tangent,
                 "asin": lambda x: math.asin(x) / factor, "acos": lambda x: math.acos(x) / factor,
                 "atan": lambda x: math.atan(x) / factor, "sqrt": math.sqrt, "log": math.log10,
                 "ln": math.log, "exp": math.exp, "powten": lambda x: safe_power(10, x),
                 "abs": abs, "inv": lambda x: 1 / x, "factorial": factorial,
                 "square": lambda x: safe_power(x, 2), "neg": lambda x: -x}
    tokens, pos = [], 0
    expression = expression.strip().replace("pow10", "powten")
    while pos < len(expression):
        match = TOKEN.match(expression, pos)
        if not match:
            raise ValueError("Karakter atau angka tidak valid.")
        tokens.append(match.group(1) or match.group(2) or match.group(3))
        pos = match.end()
    tokens.append("")
    cursor = 0
    def parse(minimum=0, depth=0):
        nonlocal cursor
        if depth > 64:
            raise ValueError("Ekspresi terlalu bertingkat.")
        token = tokens[cursor]
        cursor += 1
        if token in ("+", "-"):
            left = parse(25, depth + 1) * (-1 if token == "-" else 1)
        elif token == "(":
            left = parse(0, depth + 1)
            if tokens[cursor] != ")":
                raise ValueError("Kurung belum lengkap.")
            cursor += 1
        elif token in functions:
            if tokens[cursor] != "(":
                raise ValueError("Fungsi membutuhkan kurung.")
            cursor += 1
            arg = parse(0, depth + 1)
            if tokens[cursor] != ")":
                raise ValueError("Kurung belum lengkap.")
            cursor += 1
            left = functions[token](arg)
        elif token in ("pi", "e", "Ans"):
            left = {"pi": math.pi, "e": math.e, "Ans": answer}[token]
        elif token and (token[0].isdigit() or token[0] == "."):
            left = finite(float(token))
            if "e" not in token.lower() and abs(left) > 9007199254740991:
                raise ValueError("Angka melampaui presisi 15 digit; gunakan notasi e atau 10ˣ.")
        else:
            raise ValueError("Ekspresi belum lengkap.")
        while tokens[cursor] in ("+", "-", "*", "/", "%", "**"):
            op = tokens[cursor]
            precedence = {"+": 10, "-": 10, "*": 20, "/": 20, "%": 20, "**": 30}[op]
            if precedence < minimum:
                break
            cursor += 1
            right = parse(precedence if op == "**" else precedence + 1, depth + 1)
            if op == "+": left += right
            elif op == "-": left -= right
            elif op == "*": left *= right
            elif op == "/": left /= right
            elif op == "%": left = math.fmod(left, right)
            else: left = safe_power(left, right)
            left = finite(left)
        return finite(left)
    try:
        result = parse()
        if tokens[cursor]:
            raise ValueError("Operator atau kurung tidak valid.")
        return result
    except (ZeroDivisionError, OverflowError, IndexError) as error:
        raise ValueError("Pembagian nol, ekspresi tidak lengkap, atau hasil di luar rentang.") from error
    except ValueError as error:
        if str(error) == "math domain error":
            raise ValueError("Nilai di luar domain fungsi.") from error
        raise


def apply_function_expression(expression, name):
    """Apply unary operations to the last operand, or start a function."""
    if not expression or expression[-1] in "+-*/%(":
        return expression + name + "("
    end = len(expression)
    if expression.endswith(")"):
        depth, start = 1, end - 2
        while start >= 0 and depth:
            depth += (expression[start] == ")") - (expression[start] == "(")
            start -= 1
        start += 1
        while start > 0 and expression[start - 1].isalpha(): start -= 1
    else:
        match = re.search(r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$|[A-Za-z]+$", expression)
        if not match: raise ValueError("Operand tidak valid.")
        start = match.start()
    if start > 0 and expression[start - 1] in "+-" and (start == 1 or expression[start - 2] in "(+*/%-"):
        start -= 1
    return expression[:start] + name + "(" + expression[start:] + ")"


def display_expression(expression):
    return expression.replace("pow10", "10^").replace("powten", "10^").replace("square", "sqr").replace("**", "^").replace("pi", "π").replace("*", "×").replace("/", "÷")


def format_scientific_result(value):
    value = finite(value)
    if value == 0: return "0"
    if abs(value) >= 1e10 or abs(value) < 1e-7:
        mantissa, exponent = f"{value:.7e}".split("e")
        return f"{mantissa.rstrip('0').rstrip('.')} × 10^{int(exponent)}"
    return f"{value:.8f}".rstrip("0").rstrip(".")


def validate_date(year, month, day):
    if any(not isinstance(v, (int, float)) or not math.isfinite(v) or int(v) != v for v in (year, month, day)):
        raise ValueError("Tanggal harus berupa bilangan bulat.")
    try: return date(int(year), int(month), int(day))
    except ValueError as error: raise ValueError("Tanggal Masehi tidak valid (tahun 1–9999).") from error


def gregorian_to_jd(year, month, day):
    return validate_date(year, month, day).toordinal() + 1721424.5


def jd_to_gregorian(jd):
    try:
        result = date.fromordinal(math.floor(finite(jd) + 0.5) - 1721425)
        return result.year, result.month, result.day
    except (OverflowError, ValueError) as error: raise ValueError("JD di luar kalender tahun 1–9999.") from error


def validate_offset(offset):
    if not math.isfinite(offset) or not -12 <= offset <= 14:
        raise ValueError("UTC harus antara −12 dan +14 jam.")
    return offset


def calculate_julian_day(year, month, day, hour=12, minute=0, second=0, utc_offset=0):
    jd = gregorian_to_jd(year, month, day)
    for value, upper in ((hour, 23), (minute, 59), (second, 59)):
        if not math.isfinite(value) or int(value) != value or not 0 <= value <= upper:
            raise ValueError("Jam harus 00–23; menit dan detik 00–59.")
    return jd + (hour + minute / 60 + second / 3600 - validate_offset(utc_offset)) / 24


def is_hijri_leap(year): return (11 * year + 14) % 30 < 11


def hijri_month_days(year, month):
    if int(year) != year or not 1 <= year <= 9665 or int(month) != month or not 1 <= month <= 12:
        raise ValueError("Tahun Hijriah 1–9665 dan bulan 1–12.")
    return 30 if month % 2 or (month == 12 and is_hijri_leap(year)) else 29


def hijri_to_jd(year, month, day):
    if int(day) != day or not 1 <= day <= hijri_month_days(year, month):
        raise ValueError("Tanggal tidak ada pada bulan Hijriah yang dipilih.")
    return EPOCH + 354 * (year - 1) + (3 + 11 * year) // 30 + math.ceil(29.5 * (month - 1)) + day - 1


def jd_to_hijri(jd):
    midnight = math.floor(finite(jd) + 0.5) - 0.5
    year = math.floor((30 * (midnight - EPOCH) + 10646) / 10631)
    hijri_month_days(year, 1)
    month = 1
    while month < 12 and midnight >= hijri_to_jd(year, month + 1, 1): month += 1
    return year, month, int(midnight - hijri_to_jd(year, month, 1) + 1)


def gregorian_to_hijri(year, month, day): return jd_to_hijri(gregorian_to_jd(year, month, day))


def get_islamic_holiday(month, day, year):
    return DATA["holidays"].get(f"{month}-{day}", "Puasa Ayyamul Bidh" if day in (13, 14, 15) and month != 9 else "")


def validate_location(lat, lon, offset=0):
    if not math.isfinite(lat) or not -90 <= lat <= 90: raise ValueError("Lintang harus antara −90 dan 90°.")
    if not math.isfinite(lon) or not -180 <= lon <= 180: raise ValueError("Bujur harus antara −180 dan 180°.")
    validate_offset(offset)


def calculate_qibla(latitude, longitude):
    validate_location(latitude, longitude)
    phi, target = math.radians(latitude), math.radians(MECCA_LAT)
    delta = math.radians(MECCA_LON - longitude)
    y = math.sin(delta)
    x = math.cos(phi) * math.tan(target) - math.sin(phi) * math.cos(delta)
    if math.hypot(x, y) < 1e-12: raise ValueError("Arah kiblat tidak unik pada koordinat ini.")
    bearing = math.degrees(math.atan2(y, x)) % 360
    hav = math.sin((target - phi) / 2) ** 2 + math.cos(phi) * math.cos(target) * math.sin(delta / 2) ** 2
    hav = min(1, max(0, hav))
    dirs = ["U", "UTL", "TL", "TTL", "T", "TTG", "TG", "STG", "S", "SBD", "BD", "BBD", "B", "BBL", "BL", "UBL"]
    return {"bearing_deg": bearing, "compass_direction": dirs[int((bearing + 11.25) / 22.5) % 16], "distance_km": 6371 * 2 * math.atan2(math.sqrt(hav), math.sqrt(1 - hav))}


def prayer_hours(lat, lon, tz, year, month, day):
    validate_location(lat, lon, tz)
    d = gregorian_to_jd(year, month, day) - 2451545
    rad, deg = math.radians, math.degrees
    g, q = (357.529 + .98560028 * d) % 360, (280.459 + .98564736 * d) % 360
    longitude = (q + 1.915 * math.sin(rad(g)) + .020 * math.sin(rad(2 * g))) % 360
    obliquity = 23.439 - .00000036 * d
    dec = math.asin(math.sin(rad(obliquity)) * math.sin(rad(longitude)))
    t = math.tan(rad(obliquity) / 2) ** 2
    eq = 4 * deg(t * math.sin(2 * rad(longitude)) - 2 * .0167086 * math.sin(rad(g)) + 4 * .0167086 * t * math.sin(rad(g)) * math.cos(2 * rad(longitude)) - .5 * t ** 2 * math.sin(4 * rad(longitude)) - 1.25 * .0167086 ** 2 * math.sin(2 * rad(g)))
    noon, phi = 12 + tz - lon / 15 - eq / 60, rad(lat)
    def angle(alt):
        divisor = math.cos(phi) * math.cos(dec)
        if abs(divisor) < 1e-12: return math.nan
        value = (math.sin(rad(alt)) - math.sin(phi) * math.sin(dec)) / divisor
        return deg(math.acos(value)) if -1 <= value <= 1 else math.nan
    sun, dawn, night = angle(-.8333) / 15, angle(-20) / 15, angle(-18) / 15
    asr = angle(deg(math.atan(1 / (1 + math.tan(abs(phi - dec)))))) / 15
    return dict(imsak=noon-dawn-1/6, fajr=noon-dawn, sunrise=noon-sun, dhuhr=noon+1/30, asr=noon+asr, maghrib=noon+sun+1/30, isha=noon+night)


def location_timezone(zone=None, offset=0):
    if zone:
        try: return ZoneInfo(zone)
        except ZoneInfoNotFoundError as error:
            raise ValueError("Data zona waktu belum tersedia. Jalankan: pip install -r requirements.txt") from error
    return timezone(timedelta(hours=validate_offset(offset)))


def prayer_schedule(lat, lon, zone=None, offset=0, now=None):
    now = now or datetime.now(timezone.utc)
    location_tz = location_timezone(zone, offset)
    local = now.astimezone(location_tz)
    events, today = [], None
    for shift in (-1, 0, 1, 2):
        day = local.date() + timedelta(days=shift)
        noon = datetime.combine(day, datetime.min.time(), location_tz) + timedelta(hours=12)
        tz = noon.utcoffset().total_seconds() / 3600
        raw = prayer_hours(lat, lon, tz, day.year, day.month, day.day)
        base = datetime.combine(day, datetime.min.time(), timezone.utc).timestamp() - tz * 3600
        if shift == 0: today = {key: "Tidak tersedia" for key, _ in PRAYERS}
        for key, label in PRAYERS:
            if math.isfinite(raw[key]):
                timestamp = base + math.floor(raw[key] * 60 + .5) * 60
                events.append(dict(key=key, label=label, timestamp=timestamp))
                if shift == 0:
                    today[key] = datetime.fromtimestamp(timestamp, location_tz).strftime("%H:%M")
    events.sort(key=lambda item: item["timestamp"])
    return dict(date=local.date(), times=today, events=events, offset=local.utcoffset().total_seconds()/3600)
