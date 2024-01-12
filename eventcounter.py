from icalendar import Calendar
from datetime import datetime
import pytz
from jinja2 import Environment, FileSystemLoader

def is_bigcommerce(email):
    return email.endswith("@bigcommerce.com")

def contains_keywords(subject, keywords):
    return any(word.lower() in subject.lower() for word in keywords)

with open('events.ics', 'rb') as file:
    calendar = Calendar.from_ical(file.read())

keywords = [
    "demo", "technical", "roadmap", "demonstration", "deep dive", "deepdive", "q&a", 
    "questions", "stencil", "catalyst", "api", "use case", "headless", "composable", 
    "SOW", "sync", "onsite", "on-site", "tech", "product", "overview", "BC"
]

bigcommerce_attendees = {}
partner_domains = {}
partner_attendees = {}
filtered_events = []
total_external_events = 0
unique_non_bigcommerce = set()
bigcommerce_event_mapping = {}
partner_event_mapping = {}
excluded_domains = {"resource.calendar.google.com", "google.com", "gmail.com"}

for component in calendar.walk():
    if component.name == "VEVENT":
        dtstart = component.get('dtstart').dt
        subject = str(component.get('summary'))
        organizer = str(component.get('organizer')).replace('mailto:', '').lower() if component.get('organizer') else ''
        attendees = component.get('attendee', [])
        if not isinstance(attendees, list):
            attendees = [attendees]
        
        attendees = [str(att).replace('mailto:', '').lower() for att in attendees if att]
        if isinstance(dtstart, datetime):
            dtstart = dtstart.astimezone(pytz.UTC)
        
        if dtstart.year == 2023 and contains_keywords(subject, keywords):
            all_emails = [organizer] + attendees
            bigcommerce_names = [email.split('@')[0].replace('.', ' ').title() for email in all_emails if is_bigcommerce(email)]

            event_filtered_emails = set(email for email in all_emails if email and not is_bigcommerce(email) and email.split('@')[-1] not in excluded_domains)
            unique_emails_for_event = set()
            partner_domains_for_event = set()

            for email in all_emails:
                domain = email.split('@')[-1]
                if not is_bigcommerce(email) and domain not in excluded_domains:
                    unique_emails_for_event.add(email)
                    partner_domains_for_event.add(domain)

            if event_filtered_emails:
                event_dict = {
                    'subject': subject,
                    'dtstart': dtstart.strftime("%Y-%m-%d %H:%M:%S"),
                    'partner_count': len(unique_emails_for_event),
                    'partner_domains': list(partner_domains_for_event),
                    'attendees': all_emails,
                    'bigcommerce_names': bigcommerce_names  # Add BigCommerce names
                }
                filtered_events.append(event_dict)

                for email in event_filtered_emails:
                    unique_non_bigcommerce.add(email)
                    domain = email.split('@')[-1]
                    if domain not in partner_domains:
                        partner_domains[domain] = {'unique_emails': set(), 'event_count': 0}
                    partner_domains[domain]['unique_emails'].add(email)
                    partner_event_mapping.setdefault(domain, []).append(event_dict)
                partner_domains[domain]['event_count'] += 1

                for email in all_emails:
                    if is_bigcommerce(email):
                        bigcommerce_attendees[email] = bigcommerce_attendees.get(email, 0) + 1
                        bigcommerce_event_mapping.setdefault(email, []).append(event_dict)
            

sorted_bigcommerce_attendees = sorted([(email.split('@')[0].replace('.', ' ').title(), count) for email, count in bigcommerce_attendees.items() if '@bigcommerce.com' in email], key=lambda x: x[1], reverse=True)[1:]
sorted_partner_attendees = sorted([(domain, len(data['unique_emails']), data['event_count']) for domain, data in partner_domains.items()], key=lambda x: x[2], reverse=True)

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.html')

html_output = template.render(
    title="Event Report",
    total_external_events=len(filtered_events),
    keywords=keywords,
    unique_non_bigcommerce=len(unique_non_bigcommerce),
    bigcommerce_attendees=sorted_bigcommerce_attendees,
    partner_attendees=sorted_partner_attendees,
    filtered_events=filtered_events,
    bigcommerce_event_mapping=bigcommerce_event_mapping,
    partner_event_mapping=partner_event_mapping
)

with open('report.html', 'w') as file:
    file.write(html_output)
