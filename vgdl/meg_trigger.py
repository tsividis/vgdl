"""
Module for sending TTL triggers to the MEG acquisition system.
"""

import datetime
import pygame
import serial
import time

BAUDRATE = 9600
ARDUINO_PORT = "/dev/tty.usbmodem101"
PLAY_CLOCK_MIN = 1
PLAY_CLOCK_MAX = 63
TRIGGER_RESET_DELAY = 5 # in milliseconds

class FakePort(object):
    def __init__(self):
        super(FakePort, self).__init__()

    def write(self, value):
        pass

class Log:
    def __init__(self, fpath, do_print=False):
        self.log_file = open(fpath, "w")
        self.do_print = do_print

    def write(self, trigger_value, msg=""):
        timestamp = datetime.datetime.utcnow().strftime('%H:%M:%S.%f')
        line = ("[%s] WRITE TRIGGER value=%d[%s] (%s)" % (
                    timestamp, ord(trigger_value), format(ord(trigger_value),'08b'), msg))
        if self.do_print:
            print(line)
        self.log_file.write(line + "\n")

    def __del__(self):
        self.log_file.close()

class MEGTrigger:
    def __init__(self, port=None, do_log=False, log_fpath=None, do_print_log=False):
        if port is not None:
            self.port = serial.Serial(port=port, baudrate=BAUDRATE) # open serial port
        else:
            self.port = FakePort() # fake object to test the code without access to a serial port
        self.do_log = do_log
        if self.do_log:
            self.log = Log(log_fpath, do_print=do_print_log)

    def send(self, do_reset=False, play_clock=None, run_start=False, run_end=False,
        block_start=False, block_end=False, instance_start=False,
        instance_end=False, play_start=False, play_end=False,
        use_new_protocol=False):

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
            t_msg = trigger_message(trigger_value, use_new_protocol=use_new_protocol)
            self.port.write(t_msg) # Send trigger value
            if self.do_log:
                self.log.write(t_msg, " ".join(log_msgs))
            if do_reset:
                # Reset all bits to zero after delay. This should be done here
                # only if the reset is not already handled by the receiving
                # device
                pygame.time.wait(RESET_DELAY)
                self.port.write(chr(0))
                if self.do_log:
                    self.log.write(chr(0), "reset")

        # Send play_clock signal separately if provided
        if ((play_clock is not None)
            and (play_clock >= PLAY_CLOCK_MIN)
            and (play_clock <= PLAY_CLOCK_MAX)):
            # Encode the play_clock value between 65 and 127
            trigger_value = 64 + play_clock
            t_msg = trigger_message(trigger_value, use_new_protocol=use_new_protocol)
            self.port.write(t_msg) # Send trigger value
            if self.do_log:
                self.log.write(t_msg, "play_clock_%d" % play_clock)
            if do_reset:
                # Reset all bits to zero after delay. This should be done here
                # only if the reset is not already handled by the receiving
                # device
                pygame.time.wait(RESET_DELAY)
                self.port.write(chr(0))
                if self.do_log:
                    self.log.write(chr(0), "reset")

# send trigger; 1 <= t < 256
def trigger_message(t, use_new_protocol=False):
    if use_new_protocol:
        return bytes([int.from_bytes(b'T'), t, ord('>')]) if t > 0 else 'R>'
    else:
        return chr(t)
