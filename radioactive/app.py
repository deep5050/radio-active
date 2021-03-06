"""
    Version of the current program, (in development mode it needs to be updated in every realease)
    and to check if an updated version available for the app or not
"""
import json

import requests
from zenlog import log


class App:
    def __init__(self):
        self.__VERSION__ = "2.4.0"  # change this on every update #
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

        except:
            log.debug("Could not fetch remote version number")


# if __name__ == "__main__":
#     get_version()
