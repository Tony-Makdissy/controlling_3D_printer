import svgpathtools as svg
import numpy as np
import time


# TODO: add a foolproof way to check if the path is closed
# TODO: test some more shapes, especially when you have a vertex intersecting with a line
# TODO: decide what to do if the file contains multiple paths, probably for-loop over them
# TODO: color code the lines according to the direction of the path
# TODO: add safety distance to the lines, check if the lines are inside the shape with a distance of 0.5mm for example

class ShapeFillLine:
    def __init__(self, path, distance=2, rotation=0):
        self.cnt = 0
        self.path = path
        self.distance = distance
        self.rotation = rotation
        # self.check_for_errors() # TODO: check if I really need this
        self.pattern = self.get_pattern_lines()
        self.intersections_points = self.get_intersections_points()
        self.filling_lines = self.get_filling_lines()

    def check_for_errors(self):
        # check if you have a path
        if type(self.path) != svg.Path:
            raise ValueError("The path should be of type svgpathtools.path.Path")
        # check if the path is closed
        if not self.path.isclosed():
            raise ValueError("The path is not closed")

    def get_pattern_lines(self, center=90 + 90j, side=360):
        x_lower_limit = center.real - side / 2
        # x_upper_limit: it should be (center.real + side/2)
        # but I need to deal with floating point errors in number_of_steps
        y_lower_limit = center.imag - side / 2
        y_upper_limit = center.imag + side / 2
        number_of_steps = int(np.ceil(side / self.distance))
        x_upper_limit = x_lower_limit + number_of_steps * self.distance
        x_coordinates = np.linspace(x_lower_limit, x_upper_limit, number_of_steps)

        lines = svg.Path()
        for x in x_coordinates:
            lines.append(svg.Line(x + y_upper_limit * 1j, x + y_lower_limit * 1j))
        lines = lines.rotated(degs=self.rotation, origin=center)

        return lines

    def get_intersections_points(self):
        """ Returns the intersection points between the path and the pattern lines as a dictionary
        where the keys are the pattern lines and the values are the intersection points
        """
        intersections = sorted(self.pattern.intersect(self.path), key=lambda x: x[0][0])
        # these intersections are sorted by the T value, which is the parameter of the pattern lines
        # for two lines p & q: if p is closer to the start of the line than q, then Tp<Tq
        # T value might be different within the same line, but it makes no difference for us

        intersections_points = dict()
        for (T1, seg1, t1), (T2, seg2, t2) in intersections:
            if t2 * (t2 - 1) == 0:
                # this means that the intersection is at the start or the end of the line
                continue

            # get the intersection point
            intersections_points[seg1] = intersections_points.get(seg1, []) + [seg1.point(t1)]

        return intersections_points

    def get_filling_lines(self):
        """ Returns the filling lines as a list of svgpathtools.path.Line objects
        """
        filling_lines = []
        direction_flag = -1
        for line, points in self.intersections_points.items():
            direction_flag *= -1
            for i in range(0, len(points)-1, 2): # TODO: check if this is correct
                if direction_flag == 1:
                    filling_lines.append(svg.Line(points[i], points[i + 1]))
                else:
                    filling_lines.append(svg.Line(points[i + 1], points[i]))

        return filling_lines



if __name__ == '__main__':
    circle_path = svg.Path(svg.Arc(start=45, radius=45 + 45j, rotation=0, large_arc=1, sweep=1, end=135),
                           svg.Arc(start=135, radius=45 + 45j, rotation=0, large_arc=1, sweep=1, end=45))
    paths, attributes, svg_attributes = svg.svg2paths2('bitmap_Layer 1_1.svg')
    wanted_path = paths[1]

    # svg.disvg(wanted_path)

    for path in [wanted_path, circle_path, paths[3]]:
        fill = ShapeFillLine(path, rotation=30)

        points = []
        for v in fill.intersections_points.values():
            points.extend(v)

        list_of_shapes = [*path,
                         *fill.pattern,
                         *fill.filling_lines]

        attributes = len(path) * [{'stroke-width': 0.1, 'stroke': '#000000', 'fill':'None'}] + \
                     len(fill.pattern) * [{'stroke-width': 0.1, 'stroke': '#00FF00', 'fill':'None'}] + \
                     len(fill.filling_lines) * [{'stroke-width': 0.1, 'stroke': '#FF00FF'}]

        svg.disvg(list_of_shapes, nodes=points, node_colors=['red'] * len(points),
                  node_radii=[1] * len(points),
                  attributes=attributes)
        time.sleep(1)

