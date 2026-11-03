"""Date/time helpers with Jalali (Persian) calendar support."""
from __future__ import annotations
from datetime import datetime, timezone, date

def gregorian_to_jalali(gy: int, gm: int, gd: int):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gy + 1 if gm > 2 else gy
    days = (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd

def jalali_to_gregorian(jy: int, jm: int, jd: int):
    if jy > 979:
        gy = 1600
        jy -= 979
    else:
        gy = 621
    days = (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + 78 + jd + (
        (jm - 1) * 31 if jm < 7 else ((jm - 7) * 30) + 186
    )
    gy += 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    sal_a = [0, 31, 29 if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0) else 28,
             31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    for i in range(1, 13):
        if gd <= sal_a[i]:
            gm = i
            break
        gd -= sal_a[i]
    return gy, gm, gd

PERSIAN_MONTHS = ["\u0641\u0631\u0648\u0631\u062f\u06cc\u0646", "\u0627\u0631\u062f\u06cc\u0628\u0647\u0634\u062a", "\u062e\u0631\u062f\u0627\u062f", "\u062a\u06cc\u0631", "\u0645\u0631\u062f\u0627\u062f", "\u0634\u0647\u0631\u06cc\u0648\u0631",
                  "\u0645\u0647\u0631", "\u0622\u0628\u0627\u0646", "\u0622\u0630\u0631", "\u062f\u06cc", "\u0628\u0647\u0645\u0646", "\u0627\u0633\u0641\u0646\u062f"]

def to_jalali_string(dt, with_time: bool = False) -> str:
    if dt is None:
        return "\u2014"
    if isinstance(dt, datetime):
        jy, jm, jd = gregorian_to_jalali(dt.year, dt.month, dt.day)
        out = f"{jd} {PERSIAN_MONTHS[jm - 1]} {jy}"
        if with_time:
            out += f" - {dt.hour:02d}:{dt.minute:02d}"
        return out
    if isinstance(dt, date):
        jy, jm, jd = gregorian_to_jalali(dt.year, dt.month, dt.day)
        return f"{jd} {PERSIAN_MONTHS[jm - 1]} {jy}"
    return str(dt)

def to_persian_digits(value) -> str:
    mapping = str.maketrans("0123456789", "\u06f0\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9")
    return str(value).translate(mapping)

def utcnow() -> datetime:
    return datetime.now(timezone.utc)
