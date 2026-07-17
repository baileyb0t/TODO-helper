#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# =========================================

# ---- dependencies {{{
import argparse
import os
import subprocess
from pathlib import Path
from sys import stdout

import pandas as pd
from loguru import logger

# }}}


# --- support methods --- {{{
def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--outdir", default=None)
    args = parser.parse_args()
    assert Path(args.input).exists()
    return args


def setuplogging(logfile):
    logger.add(
        logfile,
        colorize=True,
        format="<green>{time:YYYY-MM-DD⋅at⋅HH:mm:ss}</green>⋅<level>{message}</level>",
        level="INFO",
    )
    return 1


# }}}

# --- main --- {{{
if __name__ == "__main__":
    args = getargs()
    setuplogging("output/parse_summary.log")
    logger.info("loading repo summary data")
    less = pd.read_parquet(args.input)
    logger.info(f"setting up {args.outdir} for clones")
    subprocess.call(["mkdir", args.outdir])
    os.chdir(args.outdir)
    logger.info("begin cloning")
    for sshurl in less.sshurl.values:
        clone = ["git", "clone", sshurl]
        subprocess.Popen(clone)
    logger.info("done")
# }}}

# done.
