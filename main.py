import shape_fill
import svgpathtools as svg
import simple_shapes_generator as ssg
import time
from printing_command_for_single_layer import printer_commands
import os

if __name__ == '__main__':
    # TODO: create a simple GUI

    circle = ssg.shape_gen(shape="circle", center=90 + 90j, factor=6, rotation=0).get_shape()
    path = circle

    # # or
    # square = ssg.shape_gen(shape="square", center=90 + 90j, factor=6, rotation=30).get_shape()
    # path = square

    # # or
    # paths, attributes, svg_attributes = svg.svg2paths2('svg_test.svg')
    # path = paths[0]


    fill = shape_fill.ShapeFillLine(path, rotation=45, distance=1)
    shapes = [*fill.filling_lines, *path]

    svg.disvg(shapes)
    time.sleep(1)

    commands = printer_commands(mode="injection")

    commands.comment("go to the correct height")
    commands.fast_movement(z=3, speed=10)

    # TODO: should I take the print head to the start of the first line?

    for line in fill.filling_lines:
        commands.comment("Start of line")
        commands.fast_movement(complex=line.start, speed=10)
        commands.inject_on_line(start=line.start, end=line.end,
                                between_injection_length=0.5, injection_speed=200,
                                transverse_speed=300, halt_time=400,
                                injection_direction="down", injection_depth=0.5)
        # TODO: create a function that takes the parameters that Mari-bel wants and returns the appropriate parameters for the injection

    commands.comment("left up")
    commands.fast_movement(z=50, speed=10)

    # create a directory for the gcode files
    dir_name = "gcode_files"
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    commands.save_gcode(f'{dir_name}/first_test_with_petri_dish.gcode')