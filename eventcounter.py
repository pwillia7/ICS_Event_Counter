from icalendar import Calendar
import pytz
from datetime import datetime, date
import re

def parse_ics(file_path):
    with open(file_path, 'rb') as f:
        cal = Calendar.from_ical(f.read())

    events_count = 0
    unique_attendees = set()
    bigcommerce_attendees_count = {}
    events_list = []
    filter_words = ['demo', 'technical', 'roadmap', 'demonstration', 'deep dive', 'deepdive','q&a','questions','stencil','catalyst','api','use case','headless','composable','SOW']

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
                re.search('|'.join(filter_words), summary, re.IGNORECASE)):
                
                # Temporary sets for attendees
                event_attendees = set()

                # Process attendees and count bigcommerce attendees
                if attendees:
                    for attendee in attendees:
                        attendee_email = str(attendee)
                        if 'bigcommerce.com' not in attendee_email:
                            event_attendees.add(attendee_email)
                        else:
                            bigcommerce_attendees_count[attendee_email] = bigcommerce_attendees_count.get(attendee_email, 0) + 1

                # If there are relevant attendees, count the event and update sets
                if event_attendees:
                    events_count += 1
                    unique_attendees.update(event_attendees)
                    events_list.append(f"{summary} on {dtstart.strftime('%Y-%m-%d %H:%M:%S')}")

    # Generate an HTML page with flexbox layout for columns
    with open('report.html', 'w') as file:
        file.write("<html><head><title>Event Report</title>")
        file.write("<style>")
        file.write("body { font-family: Arial, sans-serif; }")
        file.write(".flex-container { display: flex; }")
        file.write(".flex-column { flex: 1; padding: 10px; }")
        file.write("h2, h3 { color: #333; }")
        file.write("ul { list-style-type: none; padding: 0; }")
        file.write("li { padding: 5px 0; }")
        file.write("</style>")
        file.write("</head><body>")
        file.write(f"<h1>Event Report</h1>")
        file.write(f"<h2>Total Events Found: {events_count}</h2>")
        file.write(f"<h3>Filter Words Used: {', '.join(filter_words)}</h3>")

        file.write("<div class='flex-container'>")
        file.write("<div class='flex-column'><h2>Events List</h2><ul>")
        for event in events_list:
            file.write(f"<li>{event}</li>")
        file.write("</ul></div>")

        file.write("<div class='flex-column'><h2>@bigcommerce.com Attendee Counts</h2><ul>")
        sorted_bigcommerce_attendees = sorted(bigcommerce_attendees_count.items(), key=lambda x: x[1], reverse=True)
        for attendee, count in sorted_bigcommerce_attendees:
            file.write(f"<li>{attendee}: {count} events</li>")
        file.write("</ul></div>")
        file.write("</div>")

        file.write("</body></html>")

    return events_count, len(unique_attendees), len(sorted_bigcommerce_attendees)

# Example usage
file_path = 'events.ics'  # Replace with your ICS file path
events_count, unique_attendees_count, bigcommerce_attendees_unique_count = parse_ics(file_path)
print(f"Report generated: report.html")
