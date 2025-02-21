class JoystickController:
    def __init__(self, joystick, move_threshold=0.7, early_stop=True):
        self.joystick = joystick
        self.nbuttons = joystick.get_numbuttons()
        self.move_threshold = move_threshold
        self.early_stop = early_stop
        self.current_direction = None
        self.last_x = 0
        self.last_y = 0

    def get_direction(self):
        x = self.joystick.get_axis(0)
        y = self.joystick.get_axis(1)

        # Determine primary movement direction
        if abs(x) > abs(y):  # Prioritize horizontal movement
            if x > self.move_threshold:
                new_direction = "right"
            elif x < -self.move_threshold:
                new_direction = "left"
            else:
                new_direction = None
        else:  # Prioritize vertical movement
            if y > self.move_threshold:
                new_direction = "down"
            elif y < -self.move_threshold:
                new_direction = "up"
            else:
                new_direction = None

        # Stop movement early if reversing direction
        if self.early_stop and (self.current_direction is not None):
            if (self.current_direction == "left" and x > self.last_x) or \
               (self.current_direction == "right" and x < self.last_x) or \
               (self.current_direction == "down" and y < self.last_y) or \
               (self.current_direction == "up" and y > self.last_y):
                new_direction = None  # Stop movement immediately

        # Store values for comparison in next frame
        self.current_direction = new_direction
        self.last_x, self.last_y = x, y

        return self.current_direction

    def anybuttonpressed(self):
        return any((self.joystick.get_button(i) > 0) for i in range(self.nbuttons))
