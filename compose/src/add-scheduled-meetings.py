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
from zoneinfo import ZoneInfo
from datetime import date, datetime
from icalendar import Calendar, Event, vCalAddress, vText
from doc import Doc
# }}}

# support methods {{{
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ics", default="../frozen/Bailey Passmore_m.bailey.passmore@gmail.com.ics")
    args = parser.parse_args()
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


def load_cal(icsname):
    with open(icsname, 'rb') as f:
        ecal = Calendar.from_ical(f.read())
    f.close()
    return ecal
# }}}

# main --- {{{
if __name__ == '__main__':

    # basic setup --- {{{
    # setup logging
    logger = get_logger(__name__, "output/add-scheduled-meetings.log")
    # arg handling
    args = get_args()
    
    ecal = load_cal(args.ics)
    
    # this process seems to work well for one-off meetings
    # but recurring meetings are formatted differently
    # and are not consistently appearing as event items in the collection
    # notebook has IN-PROGRESS solutions to this issue
    # once I figured that out, the script will actually write to the dailyfile
    events = {}
    for event in ecal.walk("VEVENT"):
        if 'SUMMARY' in event:
            info = {
                'title': str(event['SUMMARY']),
                'timestamp': event.decoded('DTSTART'),
                'date': event.decoded('DTSTART').strftime('%Y-%m-%d'),
                'time': event.decoded('DTSTART').strftime('%H:%M'),
            }
            if 'LOCATION' in event: info['location'] = str(event['LOCATION'])
            if info['date'] not in events: events[info['date']] = [info]
            else: events[info['date']].append(info)
# }}}
