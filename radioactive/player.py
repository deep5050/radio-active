""" FFplay proess handler """
import os
import sys
from shutil import which
from signal import SIGTERM
from subprocess import Popen
from time import sleep

import psutil
from zenlog import log


class Player:

    """FFPlayer handler, it holds all the attributes to properly execute ffplay
    FFmepg required to be installed seperately
    """

    def __init__(self, URL):
        self.url = URL
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

        self.process = Popen(
            [self.exe_path, "-nodisp", "-nostats", "-loglevel", "0", self.url],
            shell=False,
        )

        log.debug("player: ffplay => PID {} initiated".format(self.process.pid))

        sleep(3)  # sleeping for 3 seconds wainting for ffplay to start properly

        if self.is_active():
            self.is_playing = True
            log.info("Radio started successfully")
        else:
            log.error("Radio could not be stared, may be a dead station")
            sys.exit(0)

    def is_active(self):
        """checks for if the ffplay is still active or not,
        will be used to terminate FFPLAY when the radioactive terminates"""

        proc = psutil.Process(self.process.pid)
        if proc.status() == psutil.STATUS_ZOMBIE:
            return False
        return True

    def play(self):
        """Nothing"""
        if not self.is_playing:
            pass  # call the init function again ?

    def stop(self):
        """sends a SIGTERM to the process id of the current FFPLAY"""

        if self.is_playing:
            log.debug("Killing ffplay PID: {}".format(self.process.pid))
            os.kill(self.process.pid, SIGTERM)
        else:
            log.warn("Player: radio is not playing")
