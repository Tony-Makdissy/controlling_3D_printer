import svgpathtools as svg
import numpy as np
import time

# TODO: add a foolproof way to check if the path is closed
# TODO: test some more shapes, espicially when you have a vertex intersecting with a line
# TODO: decide what to do if the file contains multiple paths, probably for-loop over them

circle_path = svg.Path(svg.Arc(start=45, radius=45+45j, rotation=0, large_arc=1, sweep=1, end=135),
        svg.Arc(start=135, radius=45+45j, rotation=0, large_arc=1, sweep=1, end=45))
# svg.disvg(circle_path)
# time.sleep(1)

paths, attributes, svg_attributes = svg.svg2paths2('bitmap_Layer 1_1.svg')
#
# print(paths[3])
# svg.disvg(paths[3])
circle_path = paths[3] # TODO: fix this crab, it's not a circle!



distance = 2
rotation = 30
# create number of points of distance between -90 and 270
no_of_steps = int(np.ceil(360/distance))
lower_limit = -90
upper_limit = lower_limit + no_of_steps * distance
# TODO: -90 = 0 - 90 & 270 = 180 + 90 which is the printer bed size
x_points = np.linspace(lower_limit, upper_limit, no_of_steps)

lines = svg.Path()
for x in x_points:
    lines.append(svg.Line(x + 270j, x - 90j))
lines = lines.rotated(degs=rotation, origin=90+90j) # TODO: 90+90j is the center of the printer bed

# combined_path = svg.Path(*circle_path, *lines)
# svg.disvg(combined_path)
# print(lines.intersect(circle_path))

intersections = sorted(lines.intersect(circle_path), key=lambda x: x[0][0])
# print(intersections)

points_to_print = []
lines_to_print = []

for (T1, seg1, t1), (T2, seg2, t2) in intersections:
    if t2*(t2 - 1) == 0:
        continue

    points_to_print.append(seg2.point(t2))

# read every two points and create a line
for i in range(0, len(points_to_print), 2):
    if i%2 == 0:
        lines_to_print.append(svg.Line(points_to_print[i], points_to_print[i+1]))
    else:
        lines_to_print.append(svg.Line(points_to_print[i+1], points_to_print[i]))

lines_to_print = svg.Path(*lines_to_print, *circle_path)
svg.disvg(lines_to_print)