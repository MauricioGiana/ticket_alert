import pytz
from datetime import datetime, timedelta

timezone = pytz.timezone('America/Argentina/Buenos_Aires')
week_days = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']

def str_to_date(date, str='-'):
    return datetime.strptime(date, f"{str.join(['%d', '%m', '%Y'])}")

def get_zoned_date(date, str='-'):
    return timezone.localize(str_to_date(date, str))

def format_date_with_day(date):
    week_day = week_days[get_zoned_date(date, '/').weekday()]
    return f"{date} ({week_day})"

def get_locations():
    with open("locations.txt", "r") as f:
        locations = []
        for line in f:
            location_name, location_id = line.strip().split("=")
            locations.append({ "id": location_id, "name": location_name })
        return locations

locations = get_locations()
locations_map = {location["id"]: location for location in locations}

def get_location_by_id(id):
    return locations_map[id]