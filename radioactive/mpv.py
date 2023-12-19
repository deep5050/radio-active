import subprocess
import sys
from shutil import which

from zenlog import log


class MPV:
    def __init__(self):
        self.program_name = "mpv"
        self.exe_path = which(self.program_name)
        log.debug(f"{self.program_name}: {self.exe_path}")

        if self.exe_path is None:
            log.critical(f"{self.program_name} not found, install it first please")
            sys.exit(1)

        self.is_running = False
        self.process = None
        self.url = None

    def _construct_mpv_commands(self, url):
        return [self.exe_path, url]

    def start(self, url):
        self.url = url
        mpv_commands = self._construct_mpv_commands(url)

        try:
            self.process = subprocess.Popen(
                mpv_commands,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.is_running = True
            log.debug(
                f"player: {self.program_name} => PID {self.process.pid} initiated"
            )

        except Exception as e:
            log.error(f"Error while starting player: {e}")

    def stop(self):
        if self.is_running:
            self.process.kill()
            self.is_running = False

    def toggle(self):
        if self.is_running:
            self.stop()
        else:
            self.start(self.url)
