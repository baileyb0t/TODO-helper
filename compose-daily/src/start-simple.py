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
from datetime import datetime
import yaml
import holidays
from doc import Doc
# }}}

# support methods {{{
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", default="hand/rules.yml")
    parser.add_argument("--date", default=None)
    parser.add_argument("--outputdir", default="/Users/home/git/my-TODO/individual/daily")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    assert Path(args.rules).exists()
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


def format_date(from_arg, date=datetime.now()):
    if not from_arg:
        return date.replace(tzinfo=ZoneInfo('US/Pacific'))
    if '-' in date: form = datetime.strptime(date, '%Y-%m-%d')
    else: form = datetime.strptime(date, '%Y%m%d')
    return form.astimezone(ZoneInfo('US/Pacific'))


def prep_out():
    if not args.date: today = format_date(from_arg=False)
    else: today = format_date(from_arg=True, date=args.date)
    path = f"{args.outputdir}/{today.strftime('%Y-%m-%d')}"
    today = today
    return path, today


def check_holidays():
    by_county = {holidays.country_holidays(country).get(today)
                 for country in countries}
    by_market = {holidays.financial_holidays(market).get(today)
                 for market in markets}
    found = {v for v in by_county.union(by_market) if v}
    if not any(found): return None
    return found


def add_holidays(notes):
    found = check_holidays()
    label = 'National or financial holiday(s)'
    notes.insert(prefix=formats['notes'], text=f'{label}:\t{found}')
    notes.insert(prefix='', text='')
    return notes


def add_5min(notes, prompt):
    notes.insert(prefix=formats['subheader'], text=prompt)
    for i in range(1, 2):
        notes.insert(prefix=f'{i}. ', text='____________________')
    notes.insert(prefix='', text='')
    return notes
# }}}

# main --- {{{
if __name__ == '__main__':

    # basic setup --- {{{
    # setup logging
    logger = get_logger(__name__, "output/start-simple.log")
    # arg handling
    args = get_args()
    # }}}

    rules = read_yaml(args.rules)
    countries = rules['countries'].split()
    markets = rules['markets'].split()
    formats = rules['format']

    # dynamic setup
    path, today = prep_out()

    # do the thing
    notes = Doc(prefix='# ',
              text=today.strftime('%A, %d %B %Y'),
              path=path,
              dailyday=today.strftime('%Y-%m-%d'))
    notes = add_holidays(notes)
    notes = add_5min(notes, prompt="I'm grateful for...")
    notes = add_5min(notes, prompt="What would make today great?")
    notes = add_5min(notes, prompt="Media of the day")
    notes.insert(prefix='', text='')

    notes.to_json(args.output)
# }}}
