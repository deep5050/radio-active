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
                # Ensure process has time to terminate
                sleep(0.5)
                if p.is_running():
                    p.kill()
                    log.debug(f"Forcefully killing ffplay process with PID {pid}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            log.debug("Could not terminate a ffplay process!")
    if count == 0:
        log.info("No background radios are running!")


class Ffplay:
    def __init__(self, URL, volume, loglevel):
        self.program_name = "ffplay"
        self.url = URL
        self.volume = volume
        self.loglevel = loglevel
        self.is_playing = False
        self.process = None
        self.is_running = False

        self._check_ffplay_installation()
        self.start_process()

    def _check_ffplay_installation(self):
        self.exe_path = which(self.program_name)
        if self.exe_path is None:
            log.critical("FFplay not found, install it first please")
            sys.exit(1)

    def _construct_ffplay_commands(self):
        ffplay_commands = [self.exe_path, "-volume", f"{self.volume}", "-vn", self.url]

        if self.loglevel == "debug":
            ffplay_commands.extend(["-loglevel", "error"])
        else:
            ffplay_commands.extend(["-loglevel", "error", "-nodisp"])

        return ffplay_commands

    def start_process(self):
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
            log.error("Error while starting radio: {}".format(e))
            self.is_running = False
            self.is_playing = False

    def _start_error_thread(self):
        error_thread = threading.Thread(target=self._check_error_output)
        error_thread.daemon = True
        error_thread.start()

    def _check_error_output(self):
        while self.is_running and self.process and self.process.stderr:
            stderr_result = self.process.stderr.readline()
            if stderr_result:
                self._handle_error(stderr_result)
                self.is_running = False
                self.stop()
                break
            sleep(2)

    def _handle_error(self, stderr_result):
        log.error("Could not connect to the station")
        try:
            log.debug(stderr_result)
            parts = stderr_result.split(": ")
            if len(parts) > 1:
                log.error(parts[1].strip())
            else:
                log.error(stderr_result.strip())
        except Exception as e:
            log.debug("Error: {}".format(e))

    def terminate_parent_process(self):
        parent_pid = os.getppid()
        os.kill(parent_pid, signal.SIGINT)

    def is_active(self):
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
            log.debug("Process not found or error while checking status: {}".format(e))
            return False

    def play(self):
        if not self.is_playing:
            self.start_process()

    def stop(self):
        if self.is_playing and self.process:
            try:
                self.process.kill()
                self.process.wait(timeout=5)
                log.debug("Radio playback stopped successfully")
            except subprocess.TimeoutExpired:
                log.warning("Radio process did not terminate, killing...")
                self.process.kill()
            except Exception as e:
                log.error("Error while stopping radio: {}".format(e))
                raise
            finally:
                self.is_playing = False
                self.is_running = False
                self.process = None
        else:
            log.debug("Radio is not currently playing")
            self.terminate_parent_process()

    def toggle(self):
        if self.is_playing:
            log.debug("Stopping the ffplay process")
            self.is_running = False
            self.stop()
        else:
            log.debug("Starting the ffplay process")
            self.start_process()
