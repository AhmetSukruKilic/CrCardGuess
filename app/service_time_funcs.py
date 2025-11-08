import datetime as _dt
import re
from datetime import timezone

# Precompile for speed/readability
_COMPACT_ISO_RE = re.compile(
    r"""
    ^
    (?P<date>\d{8})          # YYYYMMDD
    T
    (?P<time>\d{6})          # hhmmss
    (?:\.(?P<frac>\d+))?     # .fractional (optional)
    (?P<tz>[+\-]\d{2}:?\d{2}|)?  # timezone like +0300 or +03:00 (optional)
    $
    """,
    re.VERBOSE,
)


def to_mysql_datetime(ts: str):
    dt = parse_timestamp(ts)  # returns aware if 'Z' / +/-hh:mm included
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)  # naive UTC
    return dt


def parse_timestamp(ts: str) -> _dt.datetime:
    """
    Parse a timestamp string into a datetime.
    Supports:
      - Compact: 'YYYYMMDDThhmmss[.ffffff][Z|±hhmm|±hh:mm]'
      - Regular ISO 8601 strings compatible with datetime.fromisoformat
    Returns a timezone-aware datetime when an offset/Z is present; otherwise naive.
    """
    if not ts:
        raise ValueError("Empty timestamp")

    ts = ts.strip()
    if not ts:
        raise ValueError("Empty timestamp")

    # Normalize trailing Z/z to +00:00 for fromisoformat compatibility
    if ts.endswith(("Z", "z")):
        ts = ts[:-1] + "+00:00"

    # Try compact form first: 20251107T131150.000+0000
    m = _COMPACT_ISO_RE.match(ts)
    if m:
        date = m.group("date")
        time = m.group("time")
        frac = m.group("frac") or ""
        tz = m.group("tz") or ""

        iso = f"{date[:4]}-{date[4:6]}-{date[6:8]}T{time[:2]}:{time[2:4]}:{time[4:6]}"

        if frac:
            # normalize fraction to microseconds (6 digits)
            frac = (frac + "000000")[:6]
            iso += f".{frac}"

        if tz:
            # normalize timezone +hhmm -> +hh:mm
            if len(tz) == 5 and ":" not in tz:
                tz = tz[:3] + ":" + tz[3:]
            iso += tz

        return _dt.datetime.fromisoformat(iso)

    # Fallback to ISO 8601 strings already compatible with fromisoformat
    return _dt.datetime.fromisoformat(ts)
