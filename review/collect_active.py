# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2022, GPL v2 or later
# =========================================
# TODO-helper/import/src/import.py

# ---- dependencies {{{
from pathlib import Path
from sys import stdout
import argparse
import logging
import subprocess
import yaml
from os import listdir
import hashlib
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


def get_hash(task_str):
    enc_task = str(task_str).encode()
    hash_obj = hashlib.sha1(enc_task)
    return str(hash_obj.hexdigest())


def collect_task_fs(task_dir):
    return [
        (tag, f"{task_dir}{tag}/{f}") for tag in listdir(task_dir) if '.log' not in tag
        for f in listdir(task_dir+tag) if '.yml' in f
    ]


def fillin_tasks(task_dir):
    assert Path(task_dir).exists()
    task_lib = collect_task_fs(task_dir)
    task_dfs = []
    for (tag, f) in task_lib:
        tag_tasks = read_yaml(f)
        df = pd.DataFrame(tag_tasks, columns=['task'])
        df[tag] = 1
        task_dfs.append(df)
    out = pd.concat(task_dfs).fillna(0)
    out['task_id'] = out.task.apply(get_hash)
    return out.reset_index().drop(columns='index')


def find_mult_tags(task_df):
    tag_cols = [col for col in task_df.columns if 'task' not in col]
    if (any(task_df[tag_cols].sum(axis=1) > 1)) | (any(task_df.duplicated(subset='task_id'))):
        print("tasks with multiple labels found")
    else:
        print("no tasks found with multiple labels assigned")
    task_is = task_df.loc[task_df[tag_cols].sum(axis=1) > 1].index.values
    task_ids = task_df.loc[task_df.index.isin(task_is), 'task_id'].values
    return task_ids


def final_asserts(df):
    return 1
#}}}

# ---- main {{{
if __name__ == '__main__':

    # arg handling
    args = get_args()

    # setup logging
    logger = get_logger(__name__, f"{args.input}import.log")

    # do the thing
    task_df = fillin_tasks(args.input)
    mult_tags = find_mult_tags(task_df)

    task_df.to_parquet(args.output)
    logger.info("done.")

#}}}
# done.
