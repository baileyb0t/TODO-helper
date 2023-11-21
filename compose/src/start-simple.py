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
import yaml
import holidays
from doc import Doc
# }}}

# support methods {{{
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None)
    parser.add_argument("--rules", default="hand/rules.yml")
    parser.add_argument("--outputdir", default="/Users/home/git/my-TODO/individual/daily")
    args = parser.parse_args()
    assert Path(args.rules).exists()
    assert Path(args.outputdir).exists()
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


def format_date(arg):
    if '-' in arg: form = datetime.strptime(arg, '%Y-%m-%d')
    else: form = datetime.strptime(arg, '%Y%m%d')
    return form


def prep_out():
    if not args.date: today = date.today()
    else: today = format_date(args.date)
    out_f = f"{args.outputdir}/{today.strftime('%Y-%m-%d.md')}"
    today = today.astimezone(ZoneInfo('US/Pacific'))
    return out_f, today


def check_holidays():
    by_county = {holidays.country_holidays(country).get(today) 
                 for country in countries}
    by_market = {holidays.financial_holidays(market).get(today) 
                 for market in markets}
    found = {v for v in by_county.union(by_market) if v}
    if not any(found): return None
    return found


def add_holidays(doc):
    found = check_holidays()
    label = 'Country or financial holiday(s)'
    doc.insert(prefix=formats['notes'], text=f'{label}:\t{found}')
    return doc


def write_md(fname, doc):
    with open(fname, 'w') as f:
        f.write(doc)
    return 1
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
    dailyfile, today = prep_out()

    # do the thing
    doc = Doc(prefix='# ', text=today.strftime('%A, %d %B %Y'), filename=dailyfile)
    doc = add_holidays(doc)
    

    # temporary method of outputting docs
    # ideal is to have built-in to_json method for Doc()
    assert write_md(dailyfile, doc.__repr__())
# }}}
