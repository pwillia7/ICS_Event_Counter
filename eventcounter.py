from icalendar import Calendar
import pytz
from datetime import datetime, date
import re

def parse_ics(file_path):
    with open(file_path, 'rb') as f:
        cal = Calendar.from_ical(f.read())

    events_count = 0
    events_list = []

    for component in cal.walk():
        if component.name == "VEVENT":
            summary = str(component.get('summary'))
            dtstart = component.get('dtstart').dt
            attendees = component.get('attendee')

            # Ensure dtstart is a datetime object
            if isinstance(dtstart, date) and not isinstance(dtstart, datetime):
                dtstart = datetime(dtstart.year, dtstart.month, dtstart.day, tzinfo=pytz.UTC)

            # Check if event is after 2022/12/31 and contains one of the keywords
            if (dtstart > datetime(2022, 12, 31, tzinfo=pytz.UTC) and
                re.search(r'demo|technical|roadmap|demonstration|deep dive|deepdive|q&a|questions|stencil|catalyst|API|use case|headless|composable|SOW', summary, re.IGNORECASE)):
                
                # Check if at least one attendee is not from bigcommerce.com
                if attendees and any('bigcommerce.com' not in str(attendee) for attendee in attendees):
                    events_count += 1
                    events_list.append(f"{summary} on {dtstart.strftime('%Y-%m-%d %H:%M:%S')}")

    # Write the events to a file
    with open('events_list.txt', 'w') as file:
        for event in events_list:
            file.write(f"{event}\n")

    return events_count

# Example usage
file_path = 'events.ics'  # Replace with your ICS file path
events_count = parse_ics(file_path)
print(f"Total events found: {events_count}")
