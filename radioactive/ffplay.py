"""
Module for handling FFplay process management to play radio streams.
"""

import os
import signal
import subprocess
import sys
import threading
from shutil import which
from time import sleep
from typing import Any, List, Optional

import psutil
from zenlog import log


def kill_background_ffplays() -> None:
    """
    Kill all background 'ffplay' processes started by this user.
    """
    all_processes = psutil.process_iter(attrs=["pid", "name"])
    count = 0
    # Iterate through the processes and terminate those named "ffplay"
    for process in all_processes:
        try:
            if process.info["name"] == "ffplay":
                pid = process.info["pid"]
                p = psutil.Process(pid)
                p.terminate()
                count += 1
                log.info(f"Terminated ffplay process with PID {pid}")
                if p.is_running():
                    p.kill()
                    log.debug(f"Forcefully killing ffplay process with PID {pid}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Handle exceptions, such as processes that no longer exist or access denied
            log.debug("Could not terminate a ffplay processes!")
    if count == 0:
        pass
        # log.info("No background radios are running!")


class Ffplay:
    """
    Wrapper class to manage the FFplay process for audio playback.
    """

    def __init__(self, URL: str, volume: int, loglevel: str):
        self.program_name = "ffplay"
        self.url = URL
        self.volume = volume
        self.loglevel = loglevel
        self.is_playing = False
        self.process: Optional[subprocess.Popen] = None
        self.exe_path: Optional[str] = None
        self.is_running = False

        self._check_ffplay_installation()
        self.start_process()

    def _check_ffplay_installation(self) -> None:
        """Check if ffplay is installed and available in PATH."""
        self.exe_path = which(self.program_name)
        if self.exe_path is None:
            log.critical("FFplay not found, install it first please")
            sys.exit(1)

    def _construct_ffplay_commands(self) -> List[str]:
        """Construct the command line arguments for ffplay."""
        # Ensure volume is within valid range (0-100) though ffplay accepts 0-100
        # Actually ffplay volume is 0-100

        if self.exe_path is None:
            raise RuntimeError("FFplay executable path is not set")

        ffplay_commands = [self.exe_path, "-volume", f"{self.volume}", "-vn", self.url]

        if self.loglevel == "debug":
            ffplay_commands.extend(["-loglevel", "error"])
        else:
            ffplay_commands.extend(["-loglevel", "error", "-nodisp"])

        return ffplay_commands

    def start_process(self) -> None:
        """Start the ffplay process."""
        try:
            ffplay_commands = self._construct_ffplay_commands()
            self.process = subprocess.Popen(
                ffplay_commands,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.is_running = True
            self.is_playing = True
            self._start_error_thread()

        except Exception as e:
            log.error(f"Error while starting radio: {e}")
            self.is_playing = False

    def _start_error_thread(self) -> None:
        """Start a thread to monitor stderr for errors."""
        error_thread = threading.Thread(target=self._check_error_output)
        error_thread.daemon = True
        error_thread.start()

    def _check_error_output(self) -> None:
        """Monitor stderr for errors."""
        if not self.process or not self.process.stderr:
            return

        while self.is_running:
            try:
                stderr_result = self.process.stderr.readline()
                if stderr_result:
                    self._handle_error(stderr_result)
                    self.is_running = False
                    self.stop()
                    break
            except ValueError:
                # ValueError: I/O operation on closed file.
                break
            except Exception:
                break
            sleep(0.5)

    def _handle_error(self, stderr_result: str) -> None:
        """Log the error message."""
        print()
        log.error("Could not connect to the station/stream")
        try:
            log.debug(stderr_result)
            parts = stderr_result.split(": ")
            if len(parts) > 1:
                log.error(parts[1].strip())
            else:
                log.error(stderr_result.strip())
        except Exception as e:
            log.debug(f"Error parsing stderr: {e}")
            pass

    def terminate_parent_process(self) -> None:
        """Signal the parent process (main app) to terminate."""
        parent_pid = os.getppid()
        try:
            os.kill(parent_pid, signal.SIGINT)
        except Exception as e:
            log.debug(f"Could not kill parent process: {e}")

    def is_active(self) -> bool:
        """Check if the ffplay process is currently active/running."""
        if not self.process:
            log.warning("Process is not initialized")
            return False

        try:
            proc = psutil.Process(self.process.pid)
            if proc.status() == psutil.STATUS_ZOMBIE:
                log.debug("Process is a zombie")
                return False

            if proc.status() in [psutil.STATUS_RUNNING, psutil.STATUS_SLEEPING]:
                return True

            log.warning("Process is not in an expected state")
            return False

        except (psutil.NoSuchProcess, Exception) as e:
            log.debug(f"Process not found or error checking status: {e}")
            return False

    def play(self) -> None:
        """Resume or start playback."""
        if not self.is_playing:
            self.start_process()

    def stop(self) -> None:
        """Stop playback and terminate the process."""
        if self.is_playing and self.process:
            self.is_running = False  # Stop the error thread loop
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=2)

                log.debug("Radio playback stopped successfully")
            except Exception as e:
                log.error(f"Error while stopping radio: {e}")
            finally:
                self.is_playing = False
                self.process = None
        else:
            log.debug("Radio is not currently playing")
            self.terminate_parent_process()

    def toggle(self) -> None:
        """Toggle playback state."""
        if self.is_playing:
            log.debug("Stopping the ffplay process")
            self.stop()
        else:
            log.debug("Starting the ffplay process")
            self.start_process()
