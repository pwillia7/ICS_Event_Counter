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

    with open('report.html', 'w') as file:
        file.write("<html><head><title>Event Report</title>")
        file.write("<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css'>")
        file.write("<style>")
        file.write(".list-group-item { background-color: #f8f9fa; border: 1px solid #e9ecef; }")
        file.write(".container { padding-top: 20px; }")
        file.write(".column { flex: 50%; }")
        file.write("</style>")
        file.write("</head><body>")
        file.write("<div class='container'>")
        
        file.write(f"<h1>Event Report</h1>")
        file.write(f"<p>Total External Partner Events Found: {events_count}</p>")
        file.write(f"<p>Filter Words Used: {', '.join(filter_words)}</p>")
        file.write(f"<p>Unique Non-BC Attendees Across all Events: {len(unique_non_bigcommerce_emails)}</p>")
        
        file.write("<div class='row'>")
        file.write("<div class='col-md-6'><h4>BigCommmerce Attendees:</h4><ul class='list-group mb-3'>")
        
        sorted_bigcommerce_attendees = sorted(bigcommerce_attendees_count.items(), key=lambda x: x[1], reverse=True)
        for attendee, count in sorted_bigcommerce_attendees:
            file.write(f"<li class='list-group-item'>{attendee}: {count} events</li>")
        file.write("</ul></div>")
        file.write("<div class='col-md-6'><h4>Partner Attendees:</h4><ul class='list-group mb-3'>")
        
        sorted_non_bigcommerce_domains = sorted(non_bigcommerce_domains_info.items(), key=lambda x: x[1]['event_count'], reverse=True)
        for domain, info in sorted_non_bigcommerce_domains:
            unique_attendee_count = len(info['unique_emails'])
            event_count = info['event_count']
            file.write(f"<li class='list-group-item'>@{domain}: {unique_attendee_count} attendees across {event_count} events</li>")
        file.write("</ul></div>")

        file.write("</div>")  # Closing row div

        file.write("<div class='row'>")
        file.write("<div class='col-12'><h4>Events List</h4><ul class='list-group list-group-flush'>")
        
        for event in events_list:
            file.write(f"<li>{event}</li>")
        file.write("</ul></div>")

        file.write("</div>")  # Closing container div
        file.write("</body></html>")

    return events_count, len(bigcommerce_attendees_count), len(unique_non_bigcommerce_emails)



# Example usage
file_path = 'events.ics'  # Replace with your ICS file path
events_count, bigcommerce_attendees_unique_count, unique_non_bigcommerce_emails_count = parse_ics(file_path)
print(f"Report generated: report.html")
