"""Script to test capturing joystick input from the user."""

import pygame
import time

def main():
    pygame.init()
    pygame.joystick.init()
    
    if pygame.joystick.get_count() == 0:
        print("No joystick detected.")
        return
    
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Joystick '%s' initialized." % joystick.get_name())
    
    running = True
    while running:
        for event in pygame.event.get():
            timestamp = time.strftime('%H:%M:%S', time.localtime())
            
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.JOYAXISMOTION:
                axis = event.axis
                value = event.value
                
                if axis == 0:  # Left/Right movement
                    if value < -0.5:
                        print("[%s] Joystick moved LEFT" % timestamp)
                    elif value > 0.5:
                        print("[%s] Joystick moved RIGHT" % timestamp)
                
                elif axis == 1:  # Forward/Backward movement
                    if value < -0.5:
                        print("[%s] Joystick moved FORWARD" % timestamp)
                    elif value > 0.5:
                        print("[%s] Joystick moved BACKWARD" % timestamp)
            
            elif event.type == pygame.JOYBUTTONDOWN:
                print("[%s] Button %d pressed" % (timestamp, event.button))
            
            elif event.type == pygame.JOYBUTTONUP:
                print("[%s] Button %d released" % (timestamp, event.button))

            else:
                print("[%s] Event received %s" % (timestamp, event))
    
    pygame.quit()

if __name__ == "__main__":
    main()
