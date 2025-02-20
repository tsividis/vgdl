import vgdl.meg_trigger as meg_trigger
import curses
import time

KEYS_TO_DETECT = {
    ord('1'): {'play_clock': 1},
    ord('2'): {'play_clock': 2},
    ord('3'): {'play_clock': 3},
    ord('4'): {'play_clock': 4},
    ord('5'): {'play_clock': 5},
    ord('6'): {'play_clock': 6},
    ord('7'): {'play_clock': 7},
    ord('8'): {'play_clock': 8},
    ord('9'): {'play_clock': 9},
    ord('0'): {'play_clock': 10},
    ord('q'): {'run_start': True},
    ord('w'): {'run_end': True},
    ord('e'): {'block_start': True},
    ord('r'): {'block_end': True},
    ord('t'): {'instance_start': True},
    ord('y'): {'instance_end': True},
    ord('u'): {'play_start': True},
    ord('i'): {'play_end': True}
}

FPS = 1000  # Limit event loop to given #frames per second
do_log = True
do_print_log = True
log_fpath = "trigger_logs/meg_trigger_test.txt"

def main(stdscr):
    trigger = meg_trigger.MEGTrigger(port=meg_trigger.ARDUINO_PORT, do_log=do_log, log_fpath=log_fpath, do_print_log=do_print_log)
    stdscr.nodelay(1)  # Make getch non-blocking
    stdscr.timeout(1000 // FPS)  # Set refresh rate
    
    running = True
    while running:
        key = stdscr.getch()
        if key == ord('q'):  # Allow quitting with 'q'
            running = False
        elif key in KEYS_TO_DETECT:
            print("Key pressed: %s" % chr(key))
            trigger.send(**KEYS_TO_DETECT[key])

if __name__ == "__main__":
    curses.wrapper(main)
