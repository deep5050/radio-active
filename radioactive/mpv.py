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
            log.critical(f"{self.program_name} not found. Please install it first.")
            sys.exit(1)

        self.is_running = False
        self.process = None
        self.url = None

    def _construct_mpv_commands(self, url):
        """Constructs the command to run mpv with the given URL."""
        return [self.exe_path, url]

    def start(self, url):
        """Starts the mpv player with the specified URL."""
        if not self._is_valid_url(url):
            log.error(f"Invalid URL provided: {url}")
            return

        # If player is already running, do not start another process.
        if self.is_running and self.process:
            log.debug(f"{self.program_name} is already running with PID {self.process.pid}.")
            return

        self.url = url
        mpv_commands = self._construct_mpv_commands(url)

        try:
            self.process = subprocess.Popen(
                mpv_commands,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.is_running = True
            log.debug(f"Player: {self.program_name} => PID {self.process.pid} initiated")

        except FileNotFoundError:
            log.critical(f"{self.program_name} executable not found at {self.exe_path}.")
            sys.exit(1)
        except subprocess.SubprocessError as e:
            log.error(f"Error while starting player: {e}")
        except Exception as e:
            log.error(f"Unexpected error while starting player: {e}")

    def stop(self):
        """Stops the mpv player if it is running."""
        if self.is_running and self.process:
            try:
                self.process.terminate()  # Use terminate for a graceful shutdown
                self.process.wait(timeout=10)
                log.debug(f"Player: {self.program_name} stopped.")
            except subprocess.TimeoutExpired:
                log.warning(f"{self.program_name} did not terminate gracefully, killing process.")
                self.process.kill()
                self.process.wait()
            except Exception as e:
                log.error(f"Error stopping {self.program_name}: {e}")
            finally:
                self.is_running = False
                self.process = None
        else:
            log.debug(f"Player: {self.program_name} is not running.")

    def toggle(self):
        """Toggles the mpv player state between running and stopped."""
        if self.is_running:
            self.stop()
        else:
            if self.url is None:
                log.error("No URL set; cannot start the player.")
                return
            self.start(self.url)

    def _is_valid_url(self, url):
        """Validates the provided URL."""
        if not isinstance(url, str) or not url:
            return False
        # Basic validation: check if the URL starts with http or https
        return url.startswith("http://") or url.startswith("https://")
