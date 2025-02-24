class JoystickController:
    def __init__(self, joystick, move_threshold=0.7, early_stop=True):
        self.joystick = joystick
        self.nbuttons = joystick.get_numbuttons()
        self.move_threshold = move_threshold
        self.early_stop = early_stop
        self.initialize_state()

    def initialize_state(self):
        self.direction = None
        self.x = None
        self.y = None
        self.buttonpressed = None

    def update_state(self):
        new_x = self.joystick.get_axis(0)
        new_y = self.joystick.get_axis(1)
        new_buttonpressed = any(
            (self.joystick.get_button(i) > 0) for i in range(self.nbuttons))

        # Determine primary movement direction
        if abs(new_x) > abs(new_y):  # Prioritize horizontal movement
            if new_x > self.move_threshold:
                new_direction = "right"
            elif new_x < -self.move_threshold:
                new_direction = "left"
            else:
                new_direction = None
        else:  # Prioritize vertical movement
            if new_y > self.move_threshold:
                new_direction = "down"
            elif new_y < -self.move_threshold:
                new_direction = "up"
            else:
                new_direction = None

        # Stop movement early if reversing direction
        if self.early_stop and (self.direction is not None):
            prev_x = self.x if self.x is not None else 0
            prev_y = self.y if self.y is not None else 0
            if (self.direction == "left" and new_x > prev_x) or \
               (self.direction == "right" and new_x < prev_x) or \
               (self.direction == "down" and new_y < prev_y) or \
               (self.direction == "up" and new_y > prev_y):
                new_direction = None  # Stop movement immediately

        # Store values
        self.direction = new_direction
        self.x = new_x
        self.y = new_y
        self.buttonpressed = new_buttonpressed

    def get_state(self):
        return {
            "x": self.x,
            "y": self.y,
            "direction": self.direction,
            "buttonpressed": self.buttonpressed
        }