#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2023, HRDAG, GPL v2 or later
# =========================================

# dependencies --- {{{
from pathlib import Path
from sys import stdout
import argparse
import logging
import yaml
from datetime import date, datetime
from dateutil.relativedelta import *
from zoneinfo import ZoneInfo
import pandas as pd
from icalendar import Calendar
import recurring_ical_events
import doc
# }}}

# support methods {{{
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", default="hand/rules.yml")
    parser.add_argument("--json", default=None)
    parser.add_argument("--ics", default="../calendar/output/mbp.ics")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    assert Path(args.rules).exists()
    assert Path(args.json).exists()
    assert Path(args.ics).exists()
    return args


def get_logger(sname, file_name=None):
    logger = logging.getLogger(sname)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s " +
                                  "- %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    stream_handler = logging.StreamHandler(stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    if file_name:
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def read_yaml(fname):
    with open(fname, 'r') as f:
        rules = yaml.safe_load(f)
        f.close()
    return rules


def load_cal(icsname):
    with open(icsname, 'rb') as f:
        ecal = Calendar.from_ical(f.read())
    f.close()
    return ecal


def format_dtstart(event, local='America/Los_Angeles'):
    """When we get the event start time and compare to our 9-5 work hours,
    some events get lost because they're scheduled in another timezone.

    Note:
    - event.decoded('DTSTART') returns a datetime.datetime object
    - event.get('DTSTART') returns a vDDDTypes object

    This thread might be a better longterm strategy:
    - https://stackoverflow.com/questions/1111317/how-do-i-print-a-datetime-in-the-local-timezone

    @TODO: Can you have timezone info for an all day event? Do time,tz always appear together?"""
    dtdt_start = event.decoded('DTSTART')
    if not isinstance(dtdt_start, datetime): return dtdt_start
    if pd.isna(dtdt_start.tzinfo): return dtdt_start
    formatted = dtdt_start.astimezone(ZoneInfo(local))
    return formatted


def get_event_info(event, dtstart):
    """Structure and string-format the basic extracted event information so it's ready for the markdown note."""
    if not isinstance(dtstart, datetime): time = '*all day*'
    else: time = dtstart.time().strftime('%H:%M')
    return {
        'title': str(event['SUMMARY']),
        'date': dtstart.strftime('%Y-%m-%d'),
        'time': time,
        'weekday': dtstart.strftime('%a'),
    }


def find_events(ecal, caldate):
    """Look on `ecal` for `caldate` events that are candidate scheduled meetings.

    Handles recurring events that may not otherwise appear using `icalendar` save the first occurrence.
    Note that events are only really considered if they have a title or 'SUMMARY' value."""
    events = []
    for event in recurring_ical_events.of(ecal).at(caldate):
        dtstart = format_dtstart(event=event)
        if isinstance(dtstart, datetime):
            if (dtstart.hour < 9) | (dtstart.hour > 17): continue
        if dtstart.isoweekday() > 5: continue
        if 'SUMMARY' in event:
            if any([kw.lower() in str(event['SUMMARY']).lower()
                    for kw in ('appt', 'Office Hour', ' OH')]): continue
            info = get_event_info(event, dtstart=dtstart)
            if 'LOCATION' in event:
                info['location'] = str(event['LOCATION'])
                if any([kw in info['location'].lower() for kw in ('zoom', 'teams', 'http')]):
                    meet_type = 'virtual'
                else: meet_type = 'in person'
                info['meet_type'] = meet_type
            else:
                info['location'] = 'no location set'
                info['meet_type'] = 'no location set'
            if (event['SUMMARY'].lower() == 'payroll holiday') | ('birthday' in event['SUMMARY'].lower()):
                info['location'], info['meet_type'] = '', ''
            events.append(info)
    return events


def get_events(ecal, caldate):
    """Gather the formatted core details of all candidate events and prepare collection for markdown note.

    @TODO: Think on the division of work between the `get_events()`, `find_events()`, `get_event_info()`, etc."""
    events = find_events(ecal, caldate)
    out = []
    for event in events:
        if not any(event['meet_type']):
            text = f"{event['weekday']} {event['time']}: {event['title']}"
        else: text = f"{event['weekday']} {event['time']}: {event['title']} ({event['meet_type']})"
        out.append(text)
    return sorted(out)


def add_events(notes, events):
    notes.insert(prefix=formats['header'], text='On the Calendar')
    if len(events) < 1:
        notes.insert(prefix=formats['notes'], text=None)
        return notes
    for text in events:
        notes.insert(prefix=formats['meeting'],
                     text=text)
    notes.insert(prefix='', text='')
    return notes
# }}}

# main --- {{{
if __name__ == '__main__':

    # basic setup --- {{{
    # setup logging
    logger = get_logger(__name__, "output/add-scheduled-meetings.log")
    # arg handling
    args = get_args()

    rules = read_yaml(args.rules)
    formats = rules['format']

    notes = doc.from_json(args.json)
    ecal = load_cal(args.ics)
    caldate = notes.dailyday.replace('-','')

    events = get_events(ecal, caldate)
    notes = add_events(notes, events)

    notes.to_json(args.json)
    notes.to_md(args.output)
# }}}
