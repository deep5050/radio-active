""" FFplay process handler """

import os
import sys
from shutil import which
import subprocess
from time import sleep

import psutil
from zenlog import log


class Player:

    """FFPlayer handler, it holds all the attributes to properly execute ffplay
    FFmepg required to be installed separately
    """

    def __init__(self, URL, volume):
        self.url = URL
        self.volume = volume
        self.is_playing = False
        self.process = None
        self.exe_path = None
        self.program_name = "ffplay"  # constant value

        log.debug("player: url => {}".format(self.url))
        # check if FFplay is installed
        self.exe_path = which(self.program_name)
        log.debug("FFplay: {}".format(self.exe_path))

        if self.exe_path is None:
            log.critical("FFplay not found, install it first please")
            sys.exit(1)

        try:
            self.process = subprocess.Popen(
                [self.exe_path, "-nodisp", "-nostats", "-loglevel", "0", "-volume", f"{self.volume}", self.url],
                shell=False,
            )

            log.debug("player: ffplay => PID {} initiated".format(self.process.pid))

            #sleep(3)  # sleeping for 3 seconds waiting for ffplay to start properly

            if self.is_active():
                self.is_playing = True
                log.info("Radio started successfully")
            else:
                log.error("Radio could not be stared, may be a dead station")
                raise RuntimeError("Radio startup failed")
            
        except subprocess.CalledProcessError as e:
            log.error("Error while starting radio: {}".format(e))

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

            logging.warning("Process is not in an expected state")
            return False
        except psutil.NoSuchProcess:
            log.debug("Process not found")
            return False
        except Exception as e:
            log.error("Error while checking process status: {}".format(e))
            return False


    def play(self):
        """Nothing"""
        if not self.is_playing:
            pass  # call the init function again ?

    def stop(self):
        """stop the ffplayer """

        if self.is_playing:
            try:
                self.process.terminate()  # Terminate the process gracefully
                self.process.wait(timeout=5)  # Wait for process to finish
                log.info("Radio playback stopped successfully")
            except subprocess.TimeoutExpired:
                log.warning("Radio process did not terminate, killing...")
                self.process.kill()  # Kill the process forcefully
            except Exception as e:
                log.error("Error while stopping radio: {}".format(e))
                raise
            finally:
                self.is_playing = False
                self.process = None
        else:
            log.warning("Radio is not currently playing")