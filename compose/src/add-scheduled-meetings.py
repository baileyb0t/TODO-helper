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
from zoneinfo import ZoneInfo
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


def get_event_info(event):
    return {
        'title': str(event['SUMMARY']),
        'timestamp': event.decoded('DTSTART'),
        'date': event.decoded('DTSTART').strftime('%Y-%m-%d'),
        'time': event.decoded('DTSTART').strftime('%H:%M'),
    }


def find_events(ecal, caldate):
    events = []
    for event in recurring_ical_events.of(ecal).at(caldate):
        if 'SUMMARY' in event:
            info = get_event_info(event)
            if 'LOCATION' in event: info['location'] = str(event['LOCATION'])
            events.append(info)
    return events


def get_events(ecal, caldate):
    events = find_events(ecal, caldate)
    out = []
    for event in events:
        if 'location' in event:
            if 'zoom' in event['location'].lower(): meet_type='virtual'
            else: meet_type='in person'
        else:
            meet_type='no location set'
        text = f"{event['time']} {event['title']} ({meet_type})"
        out.append(text)
    return sorted(out)


def add_events(notes, events):
    notes.insert(prefix=formats['subheader'], text='On the Calendar')
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
