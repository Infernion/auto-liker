#! /usr/bin/env python3
import argparse
import json
import logging
import pathlib
import random
import typing as tp
from time import sleep

from .instagram_api import InstagramAPI
from .telegram_api import TelegramAPI


def parse_config(path) -> tp.Dict[str, str]:
    with open(path, "rb") as config_file:
        conf = json.loads(config_file.read(), encoding="utf-8")
    return conf


def setup_logger(log_path: str = None, log_level=logging.DEBUG):
    if log_path is not None:
        log_path = pathlib.Path(log_path)
        if not log_path.is_dir():
            log_path.mkdir()
        log_path = log_path / "log_analyzer.log"

    logging.basicConfig(
        filename=log_path,
        level=log_level,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )


def bulck_create_instagram(config):
    accounts = config["INSTAGRAM"]
    return [
        InstagramAPI(
            username=account["USERNAME"],
            password=account["PASSWORD"],
            settings_dir=config["SETTINGS_DIR"],
        )
        for account in accounts
    ]


def run(config):
    tele = TelegramAPI(token=config["TELEGRAM_API_TOKEN"])
    tele_msg_fetcher_wait = 250  # secs
    instas = bulck_create_instagram(config)

    for insta in instas:
        insta.do_auth()

    posts = tele.get_new_instagram_urls_from_chat(config["TELEGRAM_CHAT_ID"])
    logging.debug("New posts available")

    while True:
        for post_url in posts:
            logging.debug(f"Start liking {post_url}")
            for insta in instas:
                insta.like_post_by_url(post_url)
                logging.info(f"Post {post_url} was liked by {insta.username}!")
                sleep(random.randint(3, 15))
            logging.debug(f"Sleeping for {tele_msg_fetcher_wait} sec...")
        sleep(tele_msg_fetcher_wait)


parser = argparse.ArgumentParser(description="Parse config")
parser.add_argument(
    "-c",
    "--config",
    type=str,
    action="store",
    dest="config",
    required=True,
    help="Path to configuration json file",
)
setup_logger(log_level=logging.DEBUG)

args = parser.parse_args()
config_path = pathlib.Path(args.config)
logging.debug(f"Config path: {config_path}")
if not config_path.exists():
    raise ValueError(f"Config path doesn't exist: \n\t{config_path}")
parsed_config = parse_config(config_path)
logging.debug(f"Parsed configs: {parsed_config}")

run(parsed_config)

try:
    run(parsed_config)
except Exception:
    logging.exception("Exception has been raised.")
