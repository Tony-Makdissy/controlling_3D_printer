import numpy as np
import warnings

# TODO: re-write all comments that specify Z values. We don't care about it.

class printer_commands:
    def __init__(self, mode):
        self.bed_temp = 60
        self.extruder_temp = 200
        self.coordinates = np.array([0, 0, 0])
        self.extruded_length = 0
        self.extruding_rate = 0.036584173
        self.safety_distance = 0.5
        self.thickness = 0.2
        self.fast_movement_speed = 5000
        self.printing_speed = 300

        self.gcode = ""
        if mode not in ["printing", "injection"]:
            raise Exception("The mode should be either 'printing' or 'injection'")
        self.prepare_printer(mode)

    def prepare_printer(self, mode):
        if mode == "printing":
            self.gcode += f"M140 S{self.bed_temp} ; Set bed temperature\n"
            self.gcode += f"M104 S{self.extruder_temp} ; Set extruder temperature\n"
            self.gcode += f"M105 ; Read current temp\n"
            self.gcode += f"M190 S{self.bed_temp} ; Wait for bed temperature to be reached\n"
            self.gcode += f"M109 S{self.extruder_temp} ; Wait for extruder temperature to be reached\n"
            self.gcode += f"M82 ;absolute extrusion mode\n"
            self.gcode += f"G28 ; home all axes\n"
            self.gcode += f"G92 E0 ; reset extruder\n"

        elif mode == "injection":
            self.gcode += f"G28 ; home all axes\n"
            self.gcode += f"G0 F100 Z50\n"
            self.gcode += f"G0 F100 X90 Y90\n"

    def save_gcode(self, path):
        with open(path, 'w') as f:
            f.write(self.gcode)

    def wait(self, milliseconds):
        if milliseconds > 0:
            self.gcode += f"G4 P{milliseconds}\n"

    def comment(self, comment):
        self.gcode += f"; {comment}\n"

    def get_coordinates(self, **kwargs) -> tuple:
        """
        Get x, y, z coordinates from the provided kwargs.

        Args:
            **kwargs: Keyword arguments containing the following optional arguments:
                point (numpy.ndarray, optional): A 3-element 1D NumPy array representing x, y, and z coordinates.
                x (float, optional): x-coordinate in mm.
                y (float, optional): y-coordinate in mm.
                z (float, optional): z-coordinate in mm.

        Notes:
             - if point and any (or all) of x, y, or z are provided, the function will use the point argument then
               x, y, or z. Overriding the point's coordinates.

        Returns:
            tuple: A tuple containing x, y, and z coordinates.

        Raises:
            Exception: If none of "point", "x", "y", or "z" is present in kwargs.
        """

        # List of required argument names
        required_arguments = ["point", "x", "y", "z", "complex"]

        # Check if at least one of the required arguments is present in kwargs
        if not any([argument in kwargs for argument in required_arguments]):
            raise Exception("You need to provide at least one of these arguments: point, x, y, z, complex")
            # I don't really need to worry about this, because if none of the arguments are provided,
            # the function will return the current coordinates. But I'm leaving it here for fool-catching.

        if "point" in kwargs:
            # Extract x, y, and z from the "point" argument
            x, y, z = kwargs["point"]
        elif "complex" in kwargs:
            # Extract x, y from the "complex" argument
            x, y, z = kwargs["complex"].real, kwargs["complex"].imag, self.coordinates[2]
        else:
            x, y, z = self.coordinates

        x = kwargs.get("x", x)
        y = kwargs.get("y", y)
        z = kwargs.get("z", z)

        return x, y, z

    def fast_movement(self, **kwargs):
        """
        Move the printer head to the specified coordinates without extruding anything.

        Args:
            **kwargs: Keyword arguments containing the following optional arguments:
                point (numpy.ndarray, optional): A 3-element 1D NumPy array representing x, y, and z coordinates.
                x (float, optional): x-coordinate in mm.
                y (float, optional): y-coordinate in mm.
                z (float, optional): z-coordinate in mm.
                fast_movement_speed (float, optional): Movement speed in mm/min. Default is self.fast_movement_speed.

        Returns:
            None

        Note:
            - This function uses the get_coordinates function internally to get the target coordinates.
            - The speed parameter specifies the movement speed of the printer head.
            - The function does not perform any checks on the validity of the provided kwargs, as it is already done
              in the get_coordinates function.

        Example:
            # Move the printer head to x=50, y=30, z=10 at a speed of 3000 mm/min
            fast_movement(x=50, y=30, z=10, speed=3000)

            # Move the printer head to a point with coordinates (70, 40, 20) at the default speed self.fast_movement_speed
            point_coordinates = np.array([70, 40, 20])
            fast_movement(point=point_coordinates)
        """
        # no need to check of my kwargs is correct, because I already did it in the get_coordinates function

        x, y, z = self.get_coordinates(**kwargs)

        # Get the movement speed from kwargs or use the default value self.fast_movement_speed
        fast_movement_speed = kwargs.get("speed", self.fast_movement_speed)

        # Append the G0 command to the gcode for fast movement
        self.gcode += f"G0 F{fast_movement_speed} X{x} Y{y} Z{z}\n"
        self.coordinates = np.array([x, y, z])

    def print_line(self, **kwargs):
        """
        Print a line segment by moving the printer head to the target coordinates and extruding filament.

        Args:
            **kwargs: Keyword arguments containing the following optional arguments:
                point (numpy.ndarray, optional): A 3-element 1D NumPy array representing x, y, and z coordinates.
                x (float, optional): x-coordinate in mm.
                y (float, optional): y-coordinate in mm.
                z (float, optional): z-coordinate in mm.
                printing_speed (float, optional): Printing speed in mm/s. Default is the class attribute 'printing_speed'.
                extruding_rate (float, optional): Extruding rate in mm. Default is the class attribute 'extruding_rate'.
                mode (str, optional): Printing mode. Options: "normal" (default), "sticky".
                waiting_time (int, optional): Waiting time in milliseconds. Default is 0.

        Returns:
            None

        Note:
            - This function uses the get_coordinates function internally to get the target coordinates.
            - The 'mode' parameter defines the printing mode. In "normal" mode, the default values for speed and
              extruding_rate are used. In "sticky" mode, custom values (200 mm/s and 0.1 mm) are used along with a
              waiting time of 500 milliseconds.
            - The 'waiting_time' parameter adds a pause of the specified milliseconds after printing the line segment.

        Example:
            # Print a line segment from current position to x=50, y=30, z=10 using default printing speed and extruding rate
            print_line(x=50, y=30, z=10)

            # Print a line segment to a point with coordinates (70, 40, 20) using custom printing speed and extruding rate
            point_coordinates = np.array([70, 40, 20])
            print_line(point=point_coordinates, speed=3000, extruding_rate=0.2, mode="normal", waiting_time=100)

            # Print a line segment in "sticky" mode, using custom values and adding a waiting time of 500 ms
            print_line(x=60, y=35, z=15, mode="sticky")
        """
        x, y, z = self.get_coordinates(**kwargs)

        # Get optional parameters or use default class attributes
        printing_speed = kwargs.get("printing_speed", self.printing_speed)
        extruding_rate = kwargs.get("extruding_rate", self.extruding_rate)
        mode = kwargs.get("mode", "normal")
        waiting_time = kwargs.get("waiting_time", 0)

        if mode == "sticky":
            # TODO: Define sticky mode and class attributes for printing speed, extruding rate, and waiting time
            printing_speed = 200
            extruding_rate = 0.1
            waiting_time = 500

        # Calculate the distance between the current coordinates and the target coordinates
        distance = np.linalg.norm(self.coordinates - np.array([x, y, z]))
        self.extruded_length += distance * extruding_rate

        # Append the G1 command to the gcode for printing the line segment
        self.gcode += f"G1 F{printing_speed} X{x} Y{y} Z{z} E{self.extruded_length}\n"

        self.wait(waiting_time)

        self.coordinates = np.array([x, y, z])

    def fast_go_to(self, **kwargs):
        """
        Perform fast movement to the specified coordinates with safety distance.

        Args:
            **kwargs: Keyword arguments containing the following optional arguments:
                point (numpy.ndarray, optional): A 3-element 1D NumPy array representing x, y, and z coordinates.
                x (float, optional): x-coordinate in mm.
                y (float, optional): y-coordinate in mm.
                z (float, optional): z-coordinate in mm.
                fast_movement_speed (float, optional): Movement speed in mm/min. Default is self.fast_movement_speed.
                safety_distance (float, optional): Safety distance in mm. Default is 0.5 mm.

        Note:
            - This function consists of three fast movements to ensure safety during the transition to the target coordinates.
            - The safety_distance parameter determines the vertical distance to move up and down for safety.

        Example:
            # Usage with individual coordinates
            fast_go_to(x=50, y=30, z=10)

            # Usage with a point as a NumPy array
            point_coordinates = np.array([70, 40, 20])
            fast_go_to(point=point_coordinates)
        """

        # Get the safety_distance from kwargs or use the default value (self.safety_distance)
        safety_distance = kwargs.get("safety_distance", self.safety_distance)

        list_of_movements = []

        # Move up for safety
        x, y, z = self.coordinates + np.array([0, 0, safety_distance])
        list_of_movements.append([x, y, z])
        # fast movement adds to the gcode, so I don't need to do it here
        # it also updates the coordinates, so I don't need to do it here

        # Move to the given coordinates with the safety distance
        x, y, z = self.get_coordinates(**kwargs) + np.array([0, 0, safety_distance])
        list_of_movements.append([x, y, z])

        # Move down to the given coordinates
        x, y, z = self.get_coordinates(**kwargs)
        list_of_movements.append([x, y, z])

        for move in list_of_movements:
            self.fast_movement(x=move[0], y=move[1], z=move[2])

    def inject_on_line(self, start, end, **kwargs):
        acceptable_args = ["injection_depth", "between_injection_length",
                           "injection_speed", "transverse_speed",
                           "halt_time", "injection_direction"]
        for arg in kwargs:
            if arg not in acceptable_args:
                raise Exception(f"Unacceptable argument: {arg}")

        xs, ys, zs = self.get_coordinates(complex=start)
        xe, ye, ze = self.get_coordinates(complex=end)

        if zs != ze:
            warnings.warn("The start and end points are not on the same z-axis")
            # meaningless warning, because I can't get z coordinates from complex!
            # but left it here for any future changes!

        between_injection_length = kwargs.get("between_injection_length", 0.5)
        injection_speed = kwargs.get("injection_speed", 100)
        transverse_speed = kwargs.get("transverse_speed", 100)
        halt_time = kwargs.get("halt_time", 100)
        injection_direction = kwargs.get("injection_direction", "up")
        injection_depth = kwargs.get("injection_depth", 0.5)
        if injection_direction not in ["up", "down"]:
            raise Exception(f"Unacceptable injection_direction: {injection_direction}"
                            f" injection_direction should be either 'up' or 'down'")

        if injection_direction == "up":
            injection_depth = -injection_depth

        # get all the points between xs,ys,zs and xe,ye,ze with a distance of between_injection_length
        ## Calculate direction vector of the line
        direction = np.array([xe - xs, ye - ys, ze - zs])
        magnitude = np.linalg.norm(direction)
        direction = direction / magnitude  # Normalize the direction vector

        ## Calculate the number of points needed
        num_points = int(magnitude / between_injection_length)

        ## Generate intermediate points along the line
        injection_points = []
        # TODO: also return the points to add them to the graph if needed
        for i in range(1, num_points + 1):  # starting from 1 because I'll go there manually
            xi = xs + i * between_injection_length * direction[0]
            yi = ys + i * between_injection_length * direction[1]
            zi = zs + i * between_injection_length * direction[2]
            injection_points.append((xi, yi, zi))

        # go to the first point
        if (self.coordinates != np.array([xs, ys, zs])).any():
            self.fast_go_to(x=xs, y=ys, z=zs, speed=transverse_speed)
        # first injection
        self.comment("first injection")
        self.fast_movement(z=zs - injection_depth, speed=injection_speed)
        self.wait(halt_time)
        self.fast_movement(z=zs, speed=injection_speed)

        # inject on the line
        for point in injection_points:
            self.fast_movement(x=point[0], y=point[1], z=point[2], speed=transverse_speed)
            self.fast_movement(z=point[2] - injection_depth, speed=injection_speed)
            self.wait(halt_time)
            self.fast_movement(z=point[2], speed=injection_speed)

        # head to the last point
        if (injection_points[-1] != np.array([xe, ye, ze])).any():
            self.comment("Going to the last point without injection")
            self.fast_go_to(x=xe, y=ye, z=ze, speed=transverse_speed)

if __name__ == '__main__':
    pass

    commands = printer_commands(mode="printing")
    commands.fast_movement(z=1, fast_movement_speed=1000)

    commands.fast_go_to(x=10, y=10, z=0.2)
    commands.print_line(x=35, y=35, mode="sticky")
    commands.fast_go_to(x=145, y=145)
    commands.print_line(x=170, y=170, mode="sticky")
    commands.fast_go_to(x=170, y=10)
    commands.print_line(x=145, y=35, mode="sticky")
    commands.fast_go_to(x=35, y=145)
    commands.print_line(x=10, y=170, mode="sticky")

    commands.fast_go_to(x=35.2, y=35.2)
    commands.print_line(x=35.2, y=144.8, mode="sticky")
    commands.print_line(x=144.8, y=144.8, mode="sticky")
    commands.print_line(x=144.8, y=35.2, mode="sticky")
    commands.print_line(x=35.4, y=35.2, mode="sticky")

    commands.fast_movement(z=2, fast_movement_speed=1000)
    commands.fast_movement(x=90, y=90)
    commands.save_gcode('test_2.gcode')
    #
    # commands.fast_go_to(90, 90, 10)
    #
    # commands.save_gcode('test_2.gcode')
