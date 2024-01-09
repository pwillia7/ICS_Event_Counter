from icalendar import Calendar
import pytz
from datetime import datetime, date
import re

def parse_ics(file_path):
    with open(file_path, 'rb') as f:
        cal = Calendar.from_ical(f.read())

    events_count = 0
    bigcommerce_attendees_count = {}
    non_bigcommerce_domains_info = {}
    unique_non_bigcommerce_emails = set()
    events_list = []
    filter_words = ['demo', 'technical', 'roadmap', 'demonstration', 'deep dive', 'deepdive', 'q&a', 'questions', 'stencil', 'catalyst', 'api', 'use case', 'headless', 'composable', 'SOW', 'sync', 'onsite', 'on-site', 'tech', 'product', 'overview', 'BC']
    email_pattern = re.compile(r"mailto:(\S+@\S+\.\S+)")

    for component in cal.walk():
        if component.name == "VEVENT":
            summary = str(component.get('summary'))
            dtstart = component.get('dtstart').dt
            organizer = component.get('organizer')
            attendees = component.get('attendee')

            # Ensure dtstart is a datetime object
            if isinstance(dtstart, date) and not isinstance(dtstart, datetime):
                dtstart = datetime(dtstart.year, dtstart.month, dtstart.day, tzinfo=pytz.UTC)

            # Check if event is after 2022/12/31 and contains one of the keywords
            if (dtstart > datetime(2022, 12, 31, tzinfo=pytz.UTC) and
                re.search('|'.join(map(re.escape, filter_words)), summary, re.IGNORECASE)):
                
                event_emails = set()

                # Add organizer email
                if organizer:
                    organizer_email_match = email_pattern.search(str(organizer))
                    if organizer_email_match:
                        event_emails.add(organizer_email_match.group(1))

                # Process attendees
                if attendees:
                    for attendee in attendees:
                        attendee_email_match = email_pattern.search(str(attendee))
                        if attendee_email_match:
                            event_emails.add(attendee_email_match.group(1))

                # Update counts
                if any('bigcommerce.com' not in email for email in event_emails):
                    events_count += 1
                    events_list.append(f"{summary} on {dtstart.strftime('%Y-%m-%d %H:%M:%S')}")
                    for email in event_emails:
                        domain = email.split('@')[-1]
                        if 'bigcommerce.com' in email:
                            bigcommerce_attendees_count[email] = bigcommerce_attendees_count.get(email, 0) + 1
                        else:
                            unique_non_bigcommerce_emails.add(email)
                            domain_info = non_bigcommerce_domains_info.setdefault(domain, {'unique_emails': set(), 'event_count': 0})
                            domain_info['unique_emails'].add(email)
                            domain_info['event_count'] += 1

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
        file.write(f"<h3>Total Unique Non-@bigcommerce.com Attendees: {len(unique_non_bigcommerce_emails)}</h3>")
        file.write("<div class='flex-container'>")
        file.write("<div class='flex-column'><h2>@bigcommerce.com Attendee Counts</h2><ul>")
        sorted_bigcommerce_attendees = sorted(bigcommerce_attendees_count.items(), key=lambda x: x[1], reverse=True)
        for attendee, count in sorted_bigcommerce_attendees:
            file.write(f"<li>{attendee}: {count} events</li>")
        file.write("</ul></div>")

        file.write("<div class='flex-column'><h2>Non-@bigcommerce.com Domain Info</h2><ul>")
        sorted_non_bigcommerce_domains = sorted(non_bigcommerce_domains_info.items(), key=lambda x: x[1]['event_count'], reverse=True)
        for domain, info in sorted_non_bigcommerce_domains:
            unique_attendee_count = len(info['unique_emails'])
            event_count = info['event_count']
            file.write(f"<li>@{domain}: {unique_attendee_count} attendees across {event_count} events</li>")
        file.write("</ul></div>")
        
        file.write("</div>")

        file.write("<h2>Events List</h2><ul>")
        for event in events_list:
            file.write(f"<li>{event}</li>")
        file.write("</ul>")

        file.write("</body></html>")

    return events_count, len(bigcommerce_attendees_count), len(unique_non_bigcommerce_emails)


# Example usage
file_path = 'events.ics'  # Replace with your ICS file path
events_count, bigcommerce_attendees_unique_count, unique_non_bigcommerce_emails_count = parse_ics(file_path)
print(f"Report generated: report.html")
