# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2022, GPL v2 or later
# =========================================
# TODO-helper/review/src/review.py

# ---- dependencies {{{
from pathlib import Path
from sys import stdout
import argparse
import logging
import subprocess
import yaml
import pandas as pd
#}}}

# ---- support methods {{{
def initial_asserts():
    return 1 


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    assert Path(args.input).exists()
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
    with open(fname, 'r') as f_handle:
        out = yaml.safe_load(f_handle)
    return out


def track_tasks(fname, data):
    with open(fname, 'a') as f:
        yaml.dump(data, f, default_flow_style=False)
        f.close()
    print(f'{fname} updated successfully, {len(data)} item(s) added.')
    return 1


def drop_curr_tasks(fname, task_list):
    curr = set(read_yaml(fname))
    inc = set(task_list)
    keep = inc - curr
    return list(keep)


def write_tasks(write_loc, task_dict):
    exists_or_mkdir(write_loc)
    if write_loc[-1] != "/":
        write_loc += "/"
    for tag, task_list in task_dict.items():
        tag_dir = write_loc + tag
        exists_or_mkdir(f"{tag_dir}")
        fname = f"{tag_dir}/todo.yml"
        if Path(fname).exists():
            print(f"checking {len(task_list)} found tasks against those in {fname}.")
            new_tasks = drop_curr_tasks(fname, task_list)
            print(f"{len(task_list) - len(new_tasks)} duplicate tasks dropped. {len(new_tasks)} waiting to be added.")
        else:
            new_tasks = task_list
        if len(new_tasks) > 0:
            track_tasks(fname, new_tasks)
        else:
            print("no new tasks found.")
    return 1


def final_asserts(df):
    return 1
#}}}

# ---- main {{{
if __name__ == '__main__':

    # arg handling
    args = get_args()

    # setup logging
    logger = get_logger(__name__, f"{args.output}/import.log")

    # do the thing
    instrs = read_textlike(args.input)
    write_tasks(args.output, task_dict)
    logger.info("done.")

#}}}
# done.
