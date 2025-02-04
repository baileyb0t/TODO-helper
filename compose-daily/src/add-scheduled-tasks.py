#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2023, HRDAG, GPL v2 or later
# =========================================

# dependencies --- {{{
from os.path import isdir, isfile
from pathlib import Path, PosixPath
from sys import stdout
import argparse
import logging
import pandas as pd
import doc
# }}}

# support methods {{{
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--taskdir", default="~/git/my-TODO/tasks")
    args = parser.parse_args()
    assert Path(args.taskdir).exists()
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


def find_taskfiles(arg):
    if isfile(arg): return PosixPath(arg)
    if isdir(arg): return [path for path in Path(arg).rglob('*.parquet')]
    return None


def prep_tasks(arg):
    fs = find_taskfiles(arg)
    assert fs != []
    assert Path(fs[0]).exists()
    out = pd.concat([pd.read_parquet(f) for f in fs])
    return out
# }}}

# main --- {{{
if __name__ == '__main__':

    # basic setup --- {{{
    # setup logging
    logger = get_logger(__name__, "output/add-scheduled-tasks.log")
    # arg handling
    args = get_args()

    # no bumps on this road yet, just some with scheduled events
    # this will soon be amended to add task lines to the dailyfile
    # can happen regardless of if recurring meetings are being added right
    tasks = prep_tasks(args.taskdir)