def print_status_bar(length, index):
    total = length
    bar_width = 40
    frac = index / total if total else 0
    filled = int(bar_width * frac)
    bar = "=" * filled + " " * (bar_width - filled)
    print(f"\r[{bar}] {frac*100:5.1f}%", end="", flush=True)
    if index == total:
        print()
