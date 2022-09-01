import os
import sys
import argparse
import configparser
from pathlib import Path

from datetime import date, timedelta

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, "../", "vendor")
sys.path.append(vendor_dir)

from . import hubstaff_client, statstable


argparser = argparse.ArgumentParser(
    prog="hubstats",
    description="Tool generating HTML activity reports from Hubstaff API",
)
argparser.add_argument(
    "--config",
    "-c",
    default=Path.home() / ".hubstats.cfg",
    dest="config_path",
    metavar="PATH",
    help="Path to configuration INI file (default: ~/.hubstats.cfg)"
)
argparser.add_argument(
    "--date",
    "-d",
    default=(date.today() - timedelta(days=1)),
    type=date.fromisoformat,
    metavar="YYYY-MM-DD",
    help="Date to pull the activities (default: yesterday)",
)
argparser.add_argument(
    "--output",
    "-o",
    default=sys.stdout,
    type=argparse.FileType('w'),
    metavar="PATH",
    help="Output file (default: STDOUT)"
)


def main(args):
    with make_http_client(args.config_path) as client:
        results = fetch_activities(client, args.date)

    activity_map = statstable.build_activity_map(results, args.date)
    statstable.render_activity_table(activity_map, args.output)


def make_http_client(cfg_path):
    cfg = load_config(cfg_path)

    organization_id = cfg.get("DEFAULT", "organization_id")
    token_mgr = hubstaff_client.ConfigTokenManager(cfg, cfg_path)

    return hubstaff_client.HubstaffClient(organization_id, token_mgr)


def load_config(cfg_path):
    if not os.path.exists(cfg_path):
        raise OSError(f"Config file {cfg_path} does not exist, aborting...")

    config = configparser.ConfigParser()
    config.read(cfg_path)
    return config


def fetch_activities(client: hubstaff_client.HubstaffClient, exact_date: date):
    return client.activities.daily_activities(exact_date, exact_date, include=("users", "projects"))


if __name__ == "__main__":
    main(argparser.parse_args())
