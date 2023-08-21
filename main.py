import shape_fill
import svgpathtools as svg
import simple_shapes_generator as ssg
import time
from printing_command_for_single_layer import printer_commands

if __name__ == '__main__':
    circle = ssg.shape_gen(shape="circle", center=90 + 90j, factor=6, rotation=0).get_shape()

    fill = shape_fill.ShapeFillLine(circle, rotation=90, distance=0.3)
    shapes = [*fill.filling_lines, *circle]

    svg.disvg(shapes)
    time.sleep(1)


    commands = printer_commands()
    commands.bed_temp = 0
    commands.extruder_temp = 0
    commands.fast_movement(x=90, y=90, z=3, fast_movement_speed=1000)

    for line in fill.filling_lines:
        commands.fast_movement(complex=line.start, fast_movement_speed=100)
        commands.fast_movement(complex=line.end, fast_movement_speed=10)


    commands.save_gcode('first_test_with_petri_dish.gcode')
