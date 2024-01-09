# Event Counter for ICS Files

## Overview
This Python script is designed to parse ICS (iCalendar) files and count events based on specific criteria. It filters events based on their summary content and attendee email addresses. By default, it looks for events occurring after a specified date (currently hardcoded but can be changed) and checks for certain keywords in the event summary. Additionally, it filters out events where all attendees are from a specific organizational email domain.

## Prerequisites
- Python 3.x
- `icalendar` library
- `pytz` library

## Installation
Clone this repository to your local machine using the following command:

```bash
git clone https://github.com/pwillia7/ICS_Event_Counter
```

Navigate to the cloned directory. To install the required Python libraries, run:

```bash
pip install icalendar pytz

```
## Usage
Place the ICS file you want to parse in the same directory as the script, or specify its path when prompted. The script can be executed with:

```bash
python event_counter.py

```
Upon execution, the script will parse the provided ICS file according to the predefined criteria. The default criteria include a date filter (events occurring after a specific date) and keyword filtering in the event summary. These parameters are hardcoded but can be easily modified in the script.

The script outputs:

* The total count of events matching the criteria.
* A text file (events_list.txt) containing the list of event names and their dates.

## Customization

You can customize the script to suit your specific needs:

* Change the date after which events are considered by modifying the datetime object in the script.
* Adjust the keywords for event summary filtering by editing the regular expression used in the script.
* Modify the domain name in the attendee email filter to match your organization's domain.

## Contributing 
Feel free to fork this repository and submit pull requests with any enhancements. For major changes, please open an issue first to discuss what you would like to change.
