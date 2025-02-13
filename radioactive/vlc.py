import subprocess
import sys
from shutil import which

from zenlog import log


class VLC:
    def __init__(self):
        self.program_name = "vlc"
        self.exe_path = which(self.program_name)
        log.debug(f"{self.program_name}: {self.exe_path}")

        if self.exe_path is None:
            log.critical(f"{self.program_name} not found, install it first please")
            sys.exit(1)

        self.is_running = False
        self.process = None
        self.url = None

    def _is_valid_url(self, url):
        """Ensure the URL is a non-empty string starting with http:// or https://."""
        if not isinstance(url, str) or not url.strip():
            return False
        return url.startswith("http://") or url.startswith("https://")

    def _construct_vlc_commands(self, url):
        return [self.exe_path, url]

    def start(self, url):
        if not self._is_valid_url(url):
            log.error(f"Invalid URL provided: {url}")
            return

        self.url = url
        vlc_commands = self._construct_vlc_commands(url)

        try:
            self.process = subprocess.Popen(
                vlc_commands,
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
        if self.is_running and self.process:
            try:
                self.process.kill()
                self.process.wait(timeout=5)
                log.debug("Player stopped successfully")
            except Exception as e:
                log.error(f"Error stopping player: {e}")
            finally:
                self.is_running = False
                self.process = None
        else:
            log.debug("Player is not running or process is not initialized")

    def toggle(self):
        if self.is_running:
            log.debug("Stopping the player")
            self.stop()
        else:
            if self.url is None or not self._is_valid_url(self.url):
                log.error("Invalid or missing URL; cannot start the player")
                return
            log.debug("Starting the player")
            self.start(self.url)
