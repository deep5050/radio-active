""" FFplay process handler """

import os
import signal
import subprocess
import sys
import threading
from shutil import which
from time import sleep

import psutil
from zenlog import log


def kill_background_ffplays():
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
        log.info("No background radios are running!")


class Player:
    """FFPlayer handler, it holds all the attributes to properly execute ffplay
    FFmepg required to be installed separately
    """

    def __init__(self, URL, volume, loglevel):
        self.url = URL
        self.volume = volume
        self.process = None
        self.exe_path = None
        self._stream_title: str = ""
        self.program_name = "ffplay"  # constant value
        self._metadata_program = "ffprobe"  # constant value
        self._exe_metadata_path = None
        self.loglevel = loglevel

        log.debug(f"player: url => {self.url}")
        # check if FFplay is installed
        self.exe_path = which(self.program_name)
        if self.exe_path is None:
            log.critical(f"{self.program_name} not found, install it first please")
            sys.exit(1)
        else:
            log.debug(f"{self.program_name}: {self.exe_path}")

        self._exe_metadata_path = which(self._metadata_program)
        if self._exe_metadata_path is None:
            log.critical(f"{self._metadata_program} not found, install it first please")
            sys.exit(1)
        else:
            log.debug(f"{self.program_name}: {self._exe_metadata_path}")
        self._start_process()

    def read_title(self):
        ffprobe_command = [
            self._exe_metadata_path,
            "-v", "error",
            "-select_streams", "a:0",
            # TODO maybe this tag is different on different stations
            "-show_entries", "format_tags=StreamTitle",
            "-of", "default=noprint_wrappers=1:nokey=1",
            self.url
        ]
        try:
            ffprobe_proc = subprocess.Popen(
                ffprobe_command,
                shell=False,
                stdout=subprocess.PIPE,  # Capture standard output
                stderr=subprocess.PIPE,  # Capture standard error
                text=True,  # Use text mode to capture strings
            )
            title = ""
            for line in ffprobe_proc.stdout:
                title += line
            # truncate trailing \n
            return title[:-1] if title[-1] == "\n" else title
        except Exception as e:
            # Handle exceptions that might occur during process setup
            log.error(f"Error while reading current track: {e}")
            return f"Error while reading current track: {e}"

    def _start_process(self):
        ffplay_commands = [
            self.exe_path,
            "-volume",
            f"{self.volume}",
            "-vn",  # no video playback
            self.url,
        ]

        if self.loglevel == "debug":
            # don't add no disp and
            ffplay_commands.append("-loglevel")
            ffplay_commands.append("error")

        else:
            ffplay_commands.append("-loglevel")
            ffplay_commands.append("error")
            ffplay_commands.append("-nodisp")
        try:
            self.process = subprocess.Popen(
                ffplay_commands,
                shell=False,
                stdout=subprocess.PIPE,  # Capture standard output
                stderr=subprocess.PIPE,  # Capture standard error
                text=True,  # Use text mode to capture strings
            )
            log.debug(f"player: {self.program_name} => PID {self.process.pid} initiated")
            # Create a thread to continuously capture and check error output
            error_thread = threading.Thread(target=self.check_error_output)
            error_thread.daemon = True
            error_thread.start()
            # Create a thread to update the stream title information
            title_update_thread = threading.Thread(target=self.update_title)
            title_update_thread.daemon = True
            title_update_thread.start()

        except Exception as e:
            # Handle exceptions that might occur during process setup
            log.error(f"Error while starting radio: {e}")

    def update_title(self):
        while self.is_playing:
            self._stream_title = self.read_title()
            sleep(1)
        self._stream_title = ""

    def check_error_output(self):
        while self.is_playing:
            stderr_result = self.process.stderr.readline()
            if stderr_result:
                print()  # pass a blank line to command for better log messages
                log.error("Could not connect to the station")
                try:
                    # try to show the debug info
                    log.debug(stderr_result)
                    # only showing the server response
                    log.error(stderr_result.split(": ")[1])
                except Exception as e:
                    log.debug(f"Error: {e}")
                    pass
                self.stop()
            sleep(2)

    def terminate_parent_process(self):
        parent_pid = os.getppid()
        print(parent_pid)
        os.kill(parent_pid, signal.SIGINT)

    def is_active(self):
        """Check if the ffplay process is still active."""
        if not self.process:
            log.warning("Process is not initialized")
            return False
        try:
            proc = psutil.Process(self.process.pid)
            if proc.status() == psutil.STATUS_ZOMBIE:
                log.debug("Process is a zombie")
                return False

            if proc.status() == psutil.STATUS_RUNNING:
                return True

            if proc.status() == psutil.STATUS_SLEEPING:
                log.debug("Process is sleeping")
                return True  # Sleeping is considered active for our purpose

            # Handle other process states if needed

            log.warning("Process is not in an expected state")
            return False
        except psutil.NoSuchProcess:
            log.debug("Process not found")
            return False
        except Exception as e:
            log.error(f"Error while checking process status: {e}")
            return False

    def play(self):
        """Play a station"""
        if not self.is_playing:
            self._start_process()

    @property
    def is_playing(self):
        return self.process

    @property
    def stream_title(self):
        return self._stream_title

    def stop(self):
        """stop the ffplayer"""
        if self.is_playing:
            ffplay_proc = self.process
            self.process = None
            try:
                ffplay_proc.terminate()  # Terminate the process gracefully
                ffplay_proc.wait(timeout=5)  # Wait for process to finish
                log.info("Radio playback stopped successfully")
            except subprocess.TimeoutExpired:
                log.warning("Radio process did not terminate, killing...")
                ffplay_proc.kill()  # Kill the process forcefully
            except Exception as e:
                log.error(f"Error while stopping radio: {e}")
                raise
        else:
            log.debug("Radio is not currently playing")
            current_pid = os.getpid()
            os.kill(current_pid, signal.SIGINT)

    def switch_url(self, url: str):
        self.stop()
        self.url = url
        self.play()
