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
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
# }}}

# support methods --- {{{
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--oauthkey", default="../dotfiles/creds/google-cal-oauth.json")
    parser.add_argument("--cached", default="output/token.json")
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


def resolvecreds(oauthkey, cached):
    # option A: recent/still working cache from an interactive session
    creds = Credentials.from_authorized_user_file(cached, SCOPES)
    assert creds
    if ~creds.valid:
        # option B: first time use or old cache file
        # requires user interaction
        flow = InstalledAppFlow.from_client_secrets_file(oauthkey, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(cached, 'w') as f: f.write(creds.to_json())
    return creds


def getcalevents(service, calid='primary', year=year):
    events = service.events().list(calendarId=calid).execute()
    out = []
    for event in events['items']:
        if str(year) not in event['start']: continue
        title = event['summary']
        s = event['start']
        out.append(event)
    return events
# }}}


# --- main {{{
if __name__ == "__main__":
    logger = get_logger(__name__, "output/oauthevents.log")
    args = get_args()

    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    year = datetime.date.today().year

    logger.info('resolving credentials, may trigger an oauth window')
    creds = resolvecreds(args.oauthkey, args.cached)

    logger.info('loading calendar')
    service = build("calendar", "v3", credentials=creds)
    events = getcalevents(service)

    logger.info('done.')
# }}}
