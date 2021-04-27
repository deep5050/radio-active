import os
import sys
from time import sleep
from signal import SIGTERM
from subprocess import Popen
from zenlog import log
import psutil


class Player:
    """FFmepg required to be installed seperately"""

    def __init__(self, URL):
        self.url = URL
        self.is_playing = False
        self.process = None

        log.debug("player: url => {}".format(self.url))

        self.process = Popen(
            ["ffplay", "-nodisp", "-nostats", "-loglevel", "error", self.url]
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
        proc = psutil.Process(self.process.pid)
        if proc.status() == psutil.STATUS_ZOMBIE:
            return False
        return True

    def play(self):
        if not self.is_playing:
            pass  # call the init function again ?

    def stop(self):
        if self.is_playing:
            log.debug("Killing ffplay PID: {}".format(self.process.pid))
            os.kill(self.process.pid, SIGTERM)
        else:
            log.warn("Player: radio is not playing")
