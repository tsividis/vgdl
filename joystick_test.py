"""Script to test capturing joystick input from the user."""

import pygame
import time

def main():
    FPS = 20 # Limit event loop to given #frames per second
    MAX_FRAMES = FPS * 60 * 60

    pygame.init()
    pygame.joystick.init()
    
    if pygame.joystick.get_count() == 0:
        print("No joystick detected.")
        return
    
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Joystick '%s' initialized." % joystick.get_name())
    
    naxes = joystick.get_numaxes()
    nbuttons = joystick.get_numbuttons()
    print("Number of axes: %d" % naxes)
    print("Number of buttons: %d" % nbuttons)

    clock = pygame.time.Clock()
    frame = 0
    
    running = True
    while running:
        frame += 1
        timestamp = (time.strftime('%H:%M:%S', time.localtime())
                + " - Frame %d" % frame)
        for event in pygame.event.get():
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

        for i in range(naxes):
            axis = joystick.get_axis(i)
            if (abs(axis) > 0):
                print("Axis %d value: %.3f" % (i, axis))

        for i in range(nbuttons):
            buttonstate = joystick.get_button(i)
            if buttonstate != 0
                print("Button %d value: %s", buttonstate)

        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()
