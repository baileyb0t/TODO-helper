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
import urllib.request
import icalendar
import recurring_ical_events
# }}}

# support methods --- {{{
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--creds", default="../../dotfiles/creds/google-cal-secret")
    parser.add_argument("--output", default="output/mpb.ics")
    args = parser.parse_args()
    assert Path(args.creds).exists()
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


def getcreds(fname):
    with open(fname, 'r') as f:
        cred = f.read()
    return cred


def load_cal(icsname):
    with open(icsname, 'rb') as f:
        ecal = icalendar.Calendar.from_ical(f.read())
    return ecal


def writeics(fname, cal):
    with open(fname, 'wb') as f:
        f.write(cal)
    return 1
# }}}


# --- main {{{
if __name__ == "__main__":
    logger = get_logger(__name__, "output/getics.log")
    args = get_args()
    
    logger.info('loading credentials')
    privatecal = getcreds(args.creds)
    logger.info('loading private calendar')
    icalb = urllib.request.urlopen(privatecal).read()
    calendar = icalendar.Calendar.from_ical(icalb)
    logger.info('writing calendar to .ics')
    writeics(args.output, icalb)
    assert load_cal(args.output) == calendar
# }}}