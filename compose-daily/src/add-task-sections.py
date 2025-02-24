#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

# dependencies --- {{{
from pathlib import Path
from sys import stdout
import argparse
import logging
import yaml
import pandas as pd
import doc
# }}}

# support methods {{{
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", default="hand/rules.yml")
    parser.add_argument("--json", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    assert Path(args.rules).exists()
    assert Path(args.json).exists()
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
# }}}

# main --- {{{
if __name__ == '__main__':

    # basic setup --- {{{
    # setup logging
    logger = get_logger(__name__, "output/add-task-sections.log")
    # arg handling
    args = get_args()

    rules = read_yaml(args.rules)
    formats = rules['format']

    notes = doc.from_json(args.json)
    notes.insert(prefix=formats['header'], text='Non-calendar, non-coding time')
    notes.insert(prefix='', text='\n')
    notes.insert(prefix=formats['header'], text='Coding time')
    notes.insert(prefix='', text='\n')

    notes.to_json(args.json)
    notes.to_md(args.output)
# }}}
