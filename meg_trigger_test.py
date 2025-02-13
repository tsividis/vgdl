"""Script to test sending TTL triggers. Triggers are sent on key presses."""

import vgdl.meg_trigger as meg_trigger
import pygame
import time

def main():
    KEYS_TO_DETECT = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                      pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0,
                      pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t,
                      pygame.K_y, pygame.K_u, pygame.K_i]
    FPS = 1000 # Limit event loop to given #frames per second

    port = None # TBD
    do_log = True
    do_print_log = True
    log_fpath = "trigger_logs/meg_trigger_test.txt"
    trigger = meg_trigger.MEGTrigger(port=port,
        do_log=do_log, log_fpath=log_fpath, do_print_log=do_print_log)

    pygame.init()

    # Window not strictly required, but it allows to quit the program
    # by closing the window
    screen = pygame.display.set_mode((300, 200))
    pygame.display.set_caption("Trigger test")

    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key in KEYS_TO_DETECT:
                    print("Key pressed: %s" % pygame.key.name(event.key))
                    if event.key == pygame.K_1:
                        trigger.send(play_clock=1)
                    elif event.key == pygame.K_2:
                        trigger.send(play_clock=2)
                    elif event.key == pygame.K_3:
                        trigger.send(play_clock=3)
                    elif event.key == pygame.K_4:
                        trigger.send(play_clock=4)
                    elif event.key == pygame.K_5:
                        trigger.send(play_clock=5)
                    elif event.key == pygame.K_6:
                        trigger.send(play_clock=6)
                    elif event.key == pygame.K_7:
                        trigger.send(play_clock=7)
                    elif event.key == pygame.K_8:
                        trigger.send(play_clock=8)
                    elif event.key == pygame.K_9:
                        trigger.send(play_clock=9)
                    elif event.key == pygame.K_0:
                        trigger.send(play_clock=10)
                    elif event.key == pygame.K_q:
                        trigger.send(run_start=True)
                    elif event.key == pygame.K_w:
                        trigger.send(run_end=True)
                    elif event.key == pygame.K_e:
                        trigger.send(block_start=True)
                    elif event.key == pygame.K_r:
                        trigger.send(block_end=True)
                    elif event.key == pygame.K_t:
                        trigger.send(instance_start=True)
                    elif event.key == pygame.K_y:
                        trigger.send(instance_end=True)
                    elif event.key == pygame.K_u:
                        trigger.send(play_start=True)
                    elif event.key == pygame.K_i:
                        trigger.send(play_end=True)

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
