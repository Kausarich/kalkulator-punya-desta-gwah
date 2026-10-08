"""Command-line interface sharing the desktop calculation engine."""
import argparse
import sys
from engine import evaluate_scientific_expression, format_scientific_result, calculate_julian_day, calculate_qibla


def normalize_calc_expression(arguments):
    """Let argparse accept a positional expression that begins with a minus sign."""
    normalized = list(arguments)
    if not normalized or normalized[0] != "calc":
        return normalized

    index = 1
    while index < len(normalized):
        token = normalized[index]
        if token == "--mode":
            index += 2
            continue
        if token == "--expression" and index + 1 < len(normalized):
            value = normalized[index + 1]
            if value.startswith("-"):
                normalized[index] = f"--expression={value}"
                del normalized[index + 1]
            index += 1
            continue
        if token.startswith("--mode=") or token in ("--help", "-h"):
            index += 1
            continue
        if token.startswith("-") and token != "--" and not token.startswith("--expression"):
            normalized[index] = f"--expression={token}"
        break
    return normalized


def main():
    parser = argparse.ArgumentParser(description="Kalkulator Desta")
    commands = parser.add_subparsers(dest="command", required=True)
    calc = commands.add_parser("calc", help="Hitung ekspresi saintifik")
    calc.add_argument("expression", nargs="?", help="Contoh: sin(90)+2**3")
    calc.add_argument("--expression", dest="expression_option", help="Ekspresi, termasuk yang diawali tanda minus")
    calc.add_argument("--mode", choices=["DEG", "RAD", "GRAD"], default="DEG")
    julian = commands.add_parser("jd", help="Konversi tanggal/waktu ke JD")
    julian.add_argument("date", help="Tanggal YYYY-MM-DD")
    julian.add_argument("--time", default="12:00:00", help="JJ:MM:DD")
    julian.add_argument("--utc", type=float, default=0, help="Offset UTC dalam jam")
    qibla = commands.add_parser("qibla", help="Arah kiblat dari koordinat")
    qibla.add_argument("latitude", type=float)
    qibla.add_argument("longitude", type=float)
    args = parser.parse_args(normalize_calc_expression(sys.argv[1:]))
    try:
        if args.command == "calc":
            if args.expression and args.expression_option:
                parser.error("Gunakan argumen ekspresi posisi atau --expression, jangan keduanya.")
            expression = args.expression_option or args.expression
            if expression is None:
                parser.error("Masukkan ekspresi kalkulator.")
            value = evaluate_scientific_expression(expression, angle_mode=args.mode)
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
