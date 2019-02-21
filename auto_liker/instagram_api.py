import datetime
import logging
import urllib

from instagram_web_api import (
    Client,
    ClientCookieExpiredError,
    ClientError,
    ClientLoginError,
)

from .settings_manager import SettingsManager


def media_id_to_code(media_id):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    short_code = ""
    media_id = int(media_id)
    while media_id > 0:
        remainder = media_id % 64
        media_id = (media_id - remainder) / 64
        short_code = alphabet[remainder] + short_code
    return short_code


def code_to_media_id(short_code):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    media_id = 0
    for letter in short_code:
        media_id = (media_id * 64) + alphabet.index(letter)

    return str(media_id)


def get_short_code_from_url(url):
    """
    Extract short code from instagram post url

    >>> get_short_code_from_url("https://www.instagram.com/p/Bt4B21FFGGs/?utm_source=ig_share_sheet&igshid
    =dn8bqmcjehlv")
    'Bt4B21FFGGs'

    """
    path = urllib.parse.urlsplit(url).path
    return path.lstrip("/p/").rstrip("/")


class InstagramSettingsManager(SettingsManager):
    def __init__(self, username, settings_dir):
        super().__init__(settings_dir=settings_dir)
        self._username = username

    @property
    def setting_file_name(self):
        return f"instagram_{self._username}"


class InstagramAPI:
    def __init__(self, username, password, settings_dir):
        self.username = username
        self._password = password
        self._api: Client
        self._settings_manager = InstagramSettingsManager(username, settings_dir)

    def __repr__(self):
        return f"InstagramAPI for {self.username}"

    def like_post_by_url(self, url):
        media_id = code_to_media_id(get_short_code_from_url(url))
        res = self._api.post_like(media_id)
        if res["status"] == "ok":
            return True

    def do_auth(self):
        try:
            self.auth()
        except ClientCookieExpiredError:
            logging.debug("Cookies has been expired. Re-login.")
            self._settings_manager.delete_setting()
            self.auth()
        except ClientLoginError as e:
            logging.exception("ClientLoginError {0!s}".format(e))
        except ClientError as e:
            logging.exception("ClientError {0!s} (Code: {1:d})".format(e.msg, e.code))
        except Exception as e:
            logging.exception("Unexpected Exception: {0!s}".format(e))

    def auth(self):
        settings = self._settings_manager.get_settings()
        client_params = dict(
            auto_patch=True,
            authenticate=True,
            username=self.username,
            password=self._password,
        )
        if not settings:
            logging.debug(
                f"Unable to find file: {self._settings_manager.setting_file_name!s}"
            )
            client_params.update(
                dict(on_login=lambda x: onlogin_callback(x, self.username))
            )
        else:
            cached_settings = self._settings_manager.get_settings()
            logging.debug(
                f"Reusing settings: {self._settings_manager.setting_file_name!s}"
            )
            client_params.update(dict(settings=cached_settings))

        self._api = Client(**client_params)

        # Show when login expires
        cookie_expiry = self._api.cookie_jar.auth_expires
        logging.debug(
            "Cookie Expiry: {0!s}".format(
                datetime.datetime.fromtimestamp(cookie_expiry).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                )
            )
        )


def onlogin_callback(api, username):
    settings_manager = InstagramSettingsManager(username)
    cache_settings = api.settings
    settings_manager.save_settings(cache_settings)
