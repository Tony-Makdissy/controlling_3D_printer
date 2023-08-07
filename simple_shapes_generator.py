import svgpathtools as svg
import numpy as np
import time


# create a class to generate simple shapes, like circles, squares, etc. using svgpathtools
class shape_gen:
    def __init__(self, shape="circle", center=0 + 0j, factor=1, rotation=0):
        self.shape_type = shape
        self.center = center
        self.factor = factor
        self.rotation = rotation

    def get_shape(self):
        if self.shape_type == "circle":
            return self.get_circle()
        elif self.shape_type == "square":
            return self.get_square()
        else:
            raise ValueError("The shape type is not valid")

    def get_circle(self):
        center = self.center
        radius = self.factor * (1 + 1j)
        rotation = self.rotation
        circle = svg.Path(svg.Arc(start=center - self.factor, radius=radius, rotation=rotation, large_arc=1, sweep=1,
                                  end=center + self.factor),
                          svg.Arc(start=center + self.factor, radius=radius, rotation=rotation, large_arc=1, sweep=1,
                                  end=center - self.factor))

        # circle = svg.Path(svg.Arc(center - radius, radius, 2 * np.pi, rotation=rotation, large_arc=False) + center)
        return circle

    def get_square(self):
        center = self.center
        half_side = self.factor / 2
        rotation = self.rotation
        x_factor = [1, 1, -1, -1]
        y_factor = [1, -1, -1, 1]
        square = svg.Path()
        for i in range(4):
            side = svg.Line(center + half_side * x_factor[i] + half_side * y_factor[i] * 1j,
                            center + half_side * x_factor[(i + 1) % 4] + half_side * y_factor[(i + 1) % 4] * 1j)
            square.append(side)
        # rotate the square
        square = square.rotated(rotation, center)

        return square


if __name__ == '__main__':
    shapes = []
    # create circles
    circle1 = shape_gen(shape="circle", center=0 + 0j, factor=1, rotation=0).get_shape()
    circle2 = shape_gen(shape="circle", center=2 + 0j, factor=1, rotation=0).get_shape()
    circle3 = shape_gen(shape="circle", center=0 + 2j, factor=1, rotation=0).get_shape()
    circle4 = shape_gen(shape="circle", center=2 + 2j, factor=1, rotation=0).get_shape()
    shapes = shapes + [circle1, circle2, circle3, circle4]

    # create squares
    square1 = shape_gen(shape="square", center=0 + 0j, factor=np.sqrt(2), rotation=45).get_shape()
    square2 = shape_gen(shape="square", center=2 + 0j, factor=np.sqrt(2), rotation=45).get_shape()
    square3 = shape_gen(shape="square", center=0 + 2j, factor=np.sqrt(2), rotation=45).get_shape()
    square4 = shape_gen(shape="square", center=2 + 2j, factor=np.sqrt(2), rotation=45).get_shape()
    shapes = shapes + [square1, square2, square3, square4]

    svg.disvg(shapes)
    time.sleep(1)
