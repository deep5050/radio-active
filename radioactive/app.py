"""
    Version of the current program, (in development mode
    it needs to be updated in every release)
    and to check if an updated version available for the app or not
"""

import json
import sys

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata


class App:
    def __init__(self):
        try:
            self.__VERSION__ = metadata.version("radio-active")
        except metadata.PackageNotFoundError:
            self.__VERSION__ = "3.0.2"  # change this on every update #
        self.pypi_api = "https://pypi.org/pypi/radio-active/json"
        self.remote_version = ""

    def get_version(self):
        """get the version number as string"""
        return self.__VERSION__

    def get_remote_version(self):
        return self.remote_version

    def is_update_available(self):
        """Checks if the user is using an outdated version of the app,
        if any updates available inform user
        """

        try:
            import requests

            remote_data = requests.get(self.pypi_api)
            remote_data = remote_data.content.decode("utf8")
            remote_data = json.loads(remote_data)
            self.remote_version = remote_data["info"]["version"]

            # compare two version number
            tup_local = tuple(map(int, self.__VERSION__.split(".")))
            tup_remote = tuple(map(int, self.remote_version.split(".")))

            if tup_remote > tup_local:
                return True
            return False

        except Exception:
            print("Could not fetch remote version number")
