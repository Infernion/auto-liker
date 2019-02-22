import codecs
import re
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))


def read(filename):
    return codecs.open(path.join(here, filename), "r", "utf-8").read()


# preventing ModuleNotFoundError caused by importing lib before installing deps
def get_version():
    version_file = read("auto_liker/__init__.py")
    try:
        version = re.findall(r"^__version__ = \"([^']+)\"\r?$", version_file, re.M)[0]
    except IndexError:
        raise RuntimeError("Unable to determine version.")

    return version


setup(
    name="auto_liker",
    version=get_version(),
    packages=["auto_liker"],
    license="Apache License, Version 2.0",
    author="Serhii Khalymon",
    author_email="",
    install_requires=["python-telegram-bot==11.1.0", "instagram-private-api==1.5.7"],
    dependency_links=[
        "git+https://git@github.com/ping/instagram_private_api.git@"
        "1.5.7#egg=instagram-private-api"
    ],
    entry_points={"console_scripts": ["auto_liker = auto_liker.__main__"]},
)
