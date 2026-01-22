import subprocess
import sys
from shutil import which

from zenlog import log


class VLC:
    def __init__(self):
        self.program_name = "vlc"
        self.exe_path = which(self.program_name)

        # Check common locations on Windows
        if self.exe_path is None and sys.platform.startswith("win"):
            import os

            common_paths = [
                os.path.join(
                    os.environ.get("ProgramFiles", "C:\\Program Files"),
                    "VideoLAN",
                    "VLC",
                    "vlc.exe",
                ),
                os.path.join(
                    os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
                    "VideoLAN",
                    "VLC",
                    "vlc.exe",
                ),
            ]
            for path in common_paths:
                if os.path.exists(path):
                    self.exe_path = path
                    break

        log.debug(f"{self.program_name}: {self.exe_path}")

        if self.exe_path is None:
            log.critical(f"{self.program_name} not found, install it first please")
            sys.exit(1)

        self.is_running = False
        self.process = None
        self.url = None

    def _construct_vlc_commands(self, url):
        return [self.exe_path, url]

    def start(self, url):
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
        if self.is_running:
            self.process.kill()
            self.is_running = False

    def toggle(self):
        if self.is_running:
            self.stop()
        else:
            self.start(self.url)

    def play(self):
        if not self.is_running and self.url:
            self.start(self.url)
