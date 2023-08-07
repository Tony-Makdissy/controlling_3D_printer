import svgpathtools as svg
import numpy as np
import time

from printing_command_for_single_layer import printer_commands
from simple_shapes_generator import shape_gen
from shape_fill import ShapeFillLine

if __name__ == '__main__':
    square = shape_gen(shape="square", center=90 + 90j, factor=80, rotation=0).get_shape()
    lines = svg.Path()
    x_points_start = [170, 170, 10, 10]
    x_points_end = [130, 130, 50, 50]
    y_points_start = [170, 10, 10, 170]
    y_points_end = [130, 50, 50, 130]
    for i in range(4):
        line = svg.Line(x_points_start[i] + y_points_start[i] * 1j, x_points_end[i] + y_points_end[i] * 1j)
        lines.append(line)
    # svg.disvg(square)
    # time.sleep(1)

    # svg.disvg(lines)
    # time.sleep(1)

    commands = printer_commands()
    commands.fast_movement(x=90, y=90, z=2, fast_movement_speed=1000)
    commands.fast_movement(z=0.2, fast_movement_speed=1000)

    commands.fast_go_to(x=10, y=10, fast_movement_speed=1000)
    commands.print_line(x=170, y=10)

    commands.fast_go_to(complex=square[0].start)

    for line in square:
        commands.print_line(complex=line.end, mode="sticky")

    for line in lines:
        commands.fast_go_to(complex=line.start)
        commands.print_line(complex=line.end, mode="sticky")


    fill = ShapeFillLine(square, distance=1, rotation=45)
    for line in fill.filling_lines:
        commands.fast_go_to(complex=line.start, fast_movement_speed=10)
        commands.print_line(complex=line.end, mode="sticky")
        commands.wait(500)

    commands.fast_movement(z=2, fast_movement_speed=1000)
    commands.fast_movement(x=90, y=90)
    commands.save_gcode('base.gcode')
