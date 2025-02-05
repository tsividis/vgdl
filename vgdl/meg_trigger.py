"""
Module for sending TTL triggers to the MEG acquisition system.
"""

import pygame
import serial
import time

TRIGGER_DURATION_MS = 5 # Duration of the TTL pulse to send for each trigger, in milliseconds
PLAY_CLOCK_MIN = 1
PLAY_CLOCK_MAX = 63

class FakePort(object):
    def __init__(self):
        super(FakePort, self).__init__()

    def write(self, value):
        pass

class Log:
    def __init__(self, fpath):
        self.log_file = open(fpath, "w")

    def write(self, trigger_value, msg=""):
        self.log_file.write("[t=%.3f] WRITE TRIGGER value=%d[%s] (%s)\n" % (
            time.time(), ord(trigger_value), format(ord(trigger_value),'08b'), msg))

    def __del__(self):
        self.log_file.close()

class MEGTrigger:
    def __init__(self, do_log=False, log_fpath=None):
        # SER_PORT_ADDR = "/dev/ttyUSB0" # update with actual serial port address
        # self.port = serial.Serial(port=SER_PORT_ADDR) # open serial port
        self.port = FakePort() # fake object to test the code without access to a serial port
        self.do_log = do_log
        if self.do_log:
            self.log = Log(log_fpath)

    def send(self, play_clock=None, run_start=False, run_end=False,
        block_start=False, block_end=False, instance_start=False,
        instance_end=False, play_start=False, play_end=False):

        # Encode structural events using bitwise OR
        trigger_value = 0
        if run_start:
            trigger_value |= 1  # Bit 0
        if run_end:
            trigger_value |= 2  # Bit 1
        if block_start:
            trigger_value |= 4  # Bit 2
        if block_end:
            trigger_value |= 8  # Bit 3
        if instance_start:
            trigger_value |= 16 # Bit 4
        if instance_end:
            trigger_value |= 32 # Bit 5
        if play_start:
            trigger_value |= 64 # Bit 6
        if play_end:
            trigger_value |= 128 # Bit 7

        if self.do_log:
            log_msgs = []
            if run_start:
                log_msgs += ["run_start"]
            if run_end:
                log_msgs += ["run_end"]
            if block_start:
                log_msgs += ["block_start"]
            if block_end:
                log_msgs += ["block_end"]
            if instance_start:
                log_msgs += ["instance_start"]
            if instance_end:
                log_msgs += ["instance_end"]
            if play_start:
                log_msgs += ["play_start"]
            if play_end:
                log_msgs += ["play_end"]

        # Send the structural trigger if it's nonzero
        if trigger_value > 0:
            self.port.write(chr(trigger_value)) # Send trigger value
            if self.do_log:
                self.log.write(chr(trigger_value), " ".join(log_msgs))
            pygame.time.wait(TRIGGER_DURATION_MS) # Hold for 5 ms
            self.port.write(chr(0))  # Reset trigger
            if self.do_log:
                self.log.write(chr(0), "reset")

        # Send play_clock signal separately if provided
        if ((play_clock is not None)
            and (play_clock >= PLAY_CLOCK_MIN)
            and (play_clock <= PLAY_CLOCK_MAX)):
            # Encode the play_clock value between 65 and 127
            trigger_value = 64 + play_clock
            self.port.write(chr(trigger_value)) # Send trigger value
            if self.do_log:
                self.log.write(chr(trigger_value), "play_clock_%d" % play_clock)
            pygame.time.wait(TRIGGER_DURATION_MS) # Hold for 5 ms
            self.port.write(chr(0))  # Reset trigger
            if self.do_log:
                self.log.write(chr(0), "reset")
