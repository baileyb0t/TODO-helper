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
from zoneinfo import ZoneInfo
from datetime import date, datetime
from doc import Doc
# }}}

# support methods {{{
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", default="hand/rules.yml")
    parser.add_argument("--date", default=None)
    parser.add_argument("--outputdir", default="/Users/home/git/my-TODO/individual/weekly")
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


def prep_out(givendate, outdir):
    if not givendate: today = format_date(from_arg=False)
    else: today = format_date(from_arg=True, date=givendate)
    path = f"{outdir}/{today.strftime('%Y-%m-%d')}"
    today = today
    return path, today
# }}}

# main --- {{{
if __name__ == '__main__':
    logger = get_logger(__name__, "output/start-simple.log")
    args = get_args()

    rules = read_yaml(args.rules)
    formats = rules['format']

    path, today = prep_out(givendate=date.today().strftime("%Y%m%d"), outdir="./")
    notes = Doc(prefix='# ',
              text=f"BP week of {today.strftime('%d %b %Y')}",
              path=path,
              weeklyday=today.strftime('%Y-%m-%d'))
    notes.insert(prefix=formats['text'], text='\n')

    notes.insert(prefix=formats['header'], text='On my plate')
    notes.insert(prefix=formats['subheader'], text='Priorities this week')
    notes.insert(prefix=formats['notes'], text='\n')
    notes.insert(prefix=formats['subheader'], text='Back-burner this week')
    notes.insert(prefix=formats['notes'], text='\n')
    notes.insert(prefix=formats['subheader'], text='Back-back-burner')
    notes.insert(prefix=formats['notes'], text='\n\n')

    notes.to_json(args.output)
# }}}
