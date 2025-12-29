from datetime import datetime
from zoneinfo import ZoneInfo

CHILE_TZ = ZoneInfo("America/Santiago")


def now_chile() -> datetime:
    return datetime.now(tz=CHILE_TZ)
