import requests
from django.conf import settings
from constance import config
import logging

logger = logging.getLogger("discord")


def post_door_swipe_to_discord(name, door, status):
    if config.ENABLE_DISCORD_INTEGRATION and config.DISCORD_DOOR_WEBHOOK:
        logger.debug("Posting door swipe to Discord!")

        url = config.DISCORD_DOOR_WEBHOOK

        json_message = {"description": "", "embeds": []}

        if status is True:
            json_message["embeds"].append(
                {
                    "description": ":unlock: {} just **successfully** swiped at {}.".format(
                        name, door
                    ),
                    "color": 5025616,
                }
            )

        elif status == "not_signed_in":
            json_message["embeds"].append(
                {
                    "description": ":x: {} swiped at {} but was rejected because they "
                    "aren't signed into site.".format(name, door),
                    "color": 5025616,
                }
            )

        elif status == "locked_out":
            json_message["embeds"].append(
                {
                    "description": ":x: {} tried to access the {} but it is currently under a "
                    "maintenance lockout.".format(name, door),
                    "color": 16007990,
                }
            )

        else:
            json_message["embeds"].append(
                {
                    "description": f":x: {name} just swiped at {door} but was **rejected**. You "
                    f"can check your"
                    f" access [here]({config.SITE_URL}/account/access/).",
                    "color": 16007990,
                }
            )

        try:
            requests.post(url, json=json_message, timeout=settings.REQUEST_TIMEOUT)
        except requests.exceptions.ReadTimeout:
            return True

    return True


def post_interlock_swipe_to_discord(name, interlock, type, time=None):
    if config.ENABLE_DISCORD_INTEGRATION and config.DISCORD_INTERLOCK_WEBHOOK:
        logger.debug("Posting interlock swipe to Discord!")
        url = config.DISCORD_INTERLOCK_WEBHOOK

        json_message = {"description": "", "embeds": []}

        if type == "activated":
            json_message["embeds"].append(
                {
                    "description": ":unlock: {} just **activated** the {}.".format(
                        name, interlock
                    ),
                    "color": 5025616,
                }
            )

        elif type == "rejected":
            json_message["embeds"].append(
                {
                    "description": f"{name} tried to activate the {interlock} but was "
                    f"**rejected**. You can check your"
                    f" access [here]({config.SITE_URL}/account/access/).",
                    "color": 16007990,
                }
            )

        elif type == "left_on":
            json_message["embeds"].append(
                {
                    "description": ":lock: The {} was just turned off by the access system because it timed out (last used by {}). It was on for {}.".format(
                        interlock, name, time
                    ),
                    "color": 16750592,
                }
            )

        elif type == "deactivated":
            json_message["embeds"].append(
                {
                    "description": ":lock: {} just **deactivated** the {}. It was on for "
                    "{}.".format(name, interlock, time),
                    "color": 5025616,
                }
            )

        elif type == "locked_out":
            json_message["embeds"].append(
                {
                    "description": "{} tried to access the {} but it is currently under a "
                    "maintenance lockout".format(name, interlock),
                    "color": 16007990,
                }
            )

        elif type == "not_signed_in":
            json_message["embeds"].append(
                {
                    "description": ":lock: {} swiped at {} but was rejected because they "
                    "aren't signed into site.".format(name, interlock),
                    "color": 5025616,
                }
            )

        try:
            requests.post(url, json=json_message, timeout=settings.REQUEST_TIMEOUT)
        except requests.exceptions.ReadTimeout:
            return True

    else:
        return True


def post_kiosk_swipe_to_discord(name, sign_in):
    if config.ENABLE_DISCORD_INTEGRATION and config.DISCORD_DOOR_WEBHOOK:
        logger.debug("Posting kiosk swipe to Discord!")
        url = config.DISCORD_DOOR_WEBHOOK

        json_message = {"description": "", "embeds": []}

        json_message["embeds"].append(
            {
                "description": f":book: {name} just signed {'in' if sign_in else 'out'} at a kiosk.",
                "color": 5025616,
            }
        )

        try:
            requests.post(url, json=json_message, timeout=settings.REQUEST_TIMEOUT)
        except requests.exceptions.ReadTimeout:
            return True

    return True


def post_purchase_to_discord(description):
    if (
        config.ENABLE_DISCORD_INTEGRATION
        and config.DISCORD_MEMBERBUCKS_PURCHASE_WEBHOOK
    ):
        logger.debug("Posting memberbucks purchase to Discord!")
        url = config.DISCORD_MEMBERBUCKS_PURCHASE_WEBHOOK

        json_message = {"description": "", "embeds": []}

        json_message["embeds"].append(
            {
                "description": f":coin: {description}",
                "color": 5025616,
            }
        )

        try:
            requests.post(url, json=json_message, timeout=settings.REQUEST_TIMEOUT)
        except requests.exceptions.ReadTimeout:
            return True

    return True


def post_reported_issue_to_discord(
    fullname, title, description, vikunja_task_url=None, trello_card_url=None
):
    if config.ENABLE_DISCORD_INTEGRATION and config.DISCORD_REPORT_ISSUE_WEBHOOK:
        logger.debug("Posting reported issue to Discord!")

        url = config.DISCORD_REPORT_ISSUE_WEBHOOK

        if vikunja_task_url or trello_card_url:
            description += (
                f"\n\n[View in Vikunja]({vikunja_task_url})" if vikunja_task_url else ""
            )
            description += (
                f"\n\n[View in Trello]({trello_card_url})" if trello_card_url else ""
            )

        json_message = {
            "content": f"{fullname} just reported a new issue!",
            "embeds": [],
        }

        json_message["embeds"].append(
            {
                "title": title,
                "description": description,
                "color": 5025616,
            }
        )
        try:
            requests.post(url, json=json_message, timeout=settings.REQUEST_TIMEOUT)
        except requests.exceptions.ReadTimeout:
            return True

    return True


def post_door_bump_to_discord(name, door):
    if config.ENABLE_DISCORD_INTEGRATION and config.DISCORD_DOOR_WEBHOOK:
        logger.debug("Posting door bump to Discord!")

        url = config.DISCORD_DOOR_WEBHOOK

        json_message = {"description": "", "embeds": []}
        json_message["embeds"].append(
            {
                "description": ":unlock: {} just bumped at {}.".format(name, door),
                "color": 5025616,
            }
        )

        try:
            requests.post(url, json=json_message, timeout=settings.REQUEST_TIMEOUT)
        except requests.exceptions.ReadTimeout:
            return True

    return True
