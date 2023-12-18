# mpv player
import subprocess
import sys
from shutil import which

from zenlog import log


class MPV:
    def __init__(self):
        # check if mpv is installed
        self.program_name = "mpv"
        self.exe_path = which(self.program_name)
        log.debug("mpv: {}".format(self.exe_path))

        if self.exe_path is None:
            log.critical("MPV not found, install it first please")
            sys.exit(1)

    def start(self, url):
        # call mpv with URL
        self.mpv_commands = [
            self.exe_path,
            url,
        ]

        try:
            self.process = subprocess.Popen(
                self.mpv_commands,
                shell=False,
                stdout=subprocess.PIPE,  # Capture standard output
                stderr=subprocess.PIPE,  # Capture standard error
                text=True,  # Use text mode to capture strings
            )
            self.is_running = True
            log.debug("player: MPV => PID {} initiated".format(self.process.pid))

        except Exception as e:
            # Handle exceptions that might occur during process setup
            log.error("Error while starting radio: {}".format(e))
