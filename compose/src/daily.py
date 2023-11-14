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
from datetime import date, datetime
import yaml
from doc import Doc
# }}}

# support methods {{{
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None)
    parser.add_argument("--rules", default="~/git/TODO-helper/composer/hand/groups.yml")
    parser.add_argument("--outputdir", default="~/git/my-TODO/individual/daily")
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


def read_yaml(yaml_file):
    """
    read in formatting rules
    """
    with open(yaml_file, 'r') as f:
        rules = yaml.safe_load(f)
        f.close()
    return rules


def format_date(arg):
    if '-' in arg: form = datetime.strptime(arg, '%Y-%m-%d')
    else: form = datetime.strptime(arg, '%Y%m%d')
    return form
# }}}

# main --- {{{
if __name__ == '__main__':

    # basic setup --- {{{
    # setup logging
    logger = get_logger(__name__, "output/daily.log")
    # arg handling
    args = get_args()
    if not args.date: today = date.today()
    else: today = format_date(args.date)
    out_f = f"{args.outputdir}/{today.strftime('%Y-%m-%d.md')}"
    # }}}

    # Reminder:
    #     Doc's first action is assigning
    #     self.head = Line(prefix=prefix, text=text)
    doc = Doc(prefix='# ', \
            text=today.strftime('%A, %d %B %Y'))
# }}}
