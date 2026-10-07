"""Command-line interface sharing the desktop calculation engine."""
import argparse
from engine import evaluate_scientific_expression, format_scientific_result, calculate_julian_day, calculate_qibla


def main():
    parser = argparse.ArgumentParser(description="Kalkulator Desta")
    commands = parser.add_subparsers(dest="command", required=True)
    calc = commands.add_parser("calc", help="Hitung ekspresi saintifik")
    calc.add_argument("expression", help="Contoh: sin(90)+2**3")
    calc.add_argument("--mode", choices=["DEG", "RAD", "GRAD"], default="DEG")
    julian = commands.add_parser("jd", help="Konversi tanggal/waktu ke JD")
    julian.add_argument("date", help="Tanggal YYYY-MM-DD")
    julian.add_argument("--time", default="12:00:00", help="JJ:MM:DD")
    julian.add_argument("--utc", type=float, default=0, help="Offset UTC dalam jam")
    qibla = commands.add_parser("qibla", help="Arah kiblat dari koordinat")
    qibla.add_argument("latitude", type=float)
    qibla.add_argument("longitude", type=float)
    args = parser.parse_args()
    try:
        if args.command == "calc":
            value = evaluate_scientific_expression(args.expression, angle_mode=args.mode)
            print(format_scientific_result(value))
        elif args.command == "jd":
            date = [int(part) for part in args.date.split("-")]
            time = [int(part) for part in args.time.split(":")]
            if len(date) != 3 or len(time) != 3:
                raise ValueError("Gunakan tanggal YYYY-MM-DD dan waktu JJ:MM:DD.")
            print(f"JD: {calculate_julian_day(*date, *time, args.utc):.6f}")
        else:
            result = calculate_qibla(args.latitude, args.longitude)
            print(f"Arah: {result['bearing_deg']:.2f}° dari utara sejati")
            print(f"Jarak: {result['distance_km']:.1f} km")
    except (ValueError, OverflowError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
