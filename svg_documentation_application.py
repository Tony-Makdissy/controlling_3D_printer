import cmath
import svgpathtools as svg
import time
print("First")
seg1 = svg.CubicBezier(300+100j, 100+100j, 200+200j, 200+300j)  # A cubic beginning at (300, 100) and ending at (200, 300)
seg2 = svg.Line(200+300j, 250+350j)  # A line beginning at (200, 300) and ending at (250, 350)
path = svg.Path(seg1, seg2)  # A path traversing the cubic and then the line

# We could alternatively created this Path object using a d-string
path_alt = svg.parse_path('M 300 100 C 100 100 200 200 200 300 L 250 350')

# Let's check that these two methods are equivalent
print(path)
print(path_alt)
print(path == path_alt)

# On a related note, the Path.d() method returns a Path object's d-string
print(path.d())
print(svg.parse_path(path.d()) == path)

print("Second")
# Let's append another to the end of it
path.append(svg.CubicBezier(250+350j, 275+350j, 250+225j, 200+100j))
print(path)

# Let's replace the first segment with a Line object
path[0] = svg.Line(200+100j, 200+300j)
print(path)

# You may have noticed that this path is connected and now is also closed (i.e. path.start == path.end)
print("path is continuous? ", path.iscontinuous())
print("path is closed? ", path.isclosed())

# The curve the path follows is not, however, smooth (differentiable)

print("path contains non-differentiable points? ", len(svg.kinks(path)) > 0)

# If we want, we can smooth these out (Experimental and only for line/cubic paths)
# Note:  smoothing will always works (except on 180 degree turns), but you may want
# to play with the maxjointsize and tightness parameters to get pleasing results
# Note also: smoothing will increase the number of segments in a path
spath = svg.smoothed_path(path)
print("spath contains non-differentiable points? ", len(svg.kinks(spath)) > 0)
print(spath)

# Let's take a quick look at the path and its smoothed relative
# The following commands will open two browser windows to display path and spaths

svg.disvg(path)
time.sleep(1)  # needed when not giving the SVGs unique names (or not using timestamp)
svg.disvg(spath)
print("Notice that path contains {} segments and spath contains {} segments."
      "".format(len(path), len(spath)))
time.sleep(1)

print("Third")
# Read SVG into a list of path objects and list of dictionaries of attributes

# paths, attributes = svg.svg2paths('bitmap_Layer 1_1.svg')

# Update: You can now also extract the svg-attributes by setting
# return_svg_attributes=True, or with the convenience function svg2paths2

paths, attributes, svg_attributes = svg.svg2paths2('bitmap_Layer 1_1.svg')

# Let's print out the first path object and the color it was in the SVG
# We'll see it is composed of two CubicBezier objects and, in the SVG file it
# came from, it was red
redpath = paths[0]
redpath_attribs = attributes[0]
print(redpath)
# print(redpath_attribs['stroke'])
svg.disvg(paths)

print("Fourth")
# Example:
b = svg.CubicBezier(300+100j, 100+100j, 200+200j, 200+300j)
p = b.poly()
print(p)
print(type(p))
# p(t) == b.point(t)
print(p(0.235) == b.point(0.235))

# What is p(t)?  It's just the cubic b written in standard form.
bpretty = r"{}*(1-t)^3 + 3*{}*(1-t)^2*t + 3*{}*(1-t)*t^2 + {}*t^3".format(*b.bpoints())
print("The CubicBezier, b.point(x) = \n\n" +
      bpretty + "\n\n" +
      "can be rewritten in standard form as \n\n" +
      str(p).replace('x','t'))

print("Fifth")
t = 0.5
### Method 1: the easy way
u1 = b.unit_tangent(t)

### Method 2: another easy way
# Note: This way will fail if it encounters a removable singularity.
u2 = b.derivative(t)/abs(b.derivative(t))

### Method 2: a third easy way
# Note: This way will also fail if it encounters a removable singularity.
dp = p.deriv()
u3 = dp(t)/abs(dp(t))

### Method 4: the removable-singularity-proof numpy.poly1d way
# Note: This is roughly how Method 1 works
dx, dy = svg.real(dp), svg.imag(dp)  # dp == dx + 1j*dy
p_mag2 = dx**2 + dy**2  # p_mag2(t) = |p(t)|**2
# Note: abs(dp) isn't a polynomial, but abs(dp)**2 is, and,
#  the limit_{t->t0}[f(t) / abs(f(t))] ==
# sqrt(limit_{t->t0}[f(t)**2 / abs(f(t))**2])
u4 = cmath.sqrt(svg.rational_limit(dp**2, p_mag2, t))

print("unit tangent check:", u1 == u2 == u3 == u4)
print("unit tangent:", u1)
# Let's do a visual check
mag = b.length()/4  # so it's not hard to see the tangent line
tangent_line = svg.Line(b.point(t), b.point(t) + mag*u1)
svg.disvg([b, tangent_line], 'bg', nodes=[b.point(t)])

print("Sixth")
# Speaking of tangents, let's add a normal vector to the picture
n = b.normal(t)
normal_line = svg.Line(b.point(t), b.point(t) + mag*n)
svg.disvg([b, tangent_line, normal_line], 'bgp', nodes=[b.point(t)])

# and let's reverse the orientation of b!
# the tangent and normal lines should be sent to their opposites
br = b.reversed()

# Let's also shift b_r over a bit to the right so we can view it next to b
# The simplest way to do this is br = br.translated(3*mag),  but let's use
# the .bpoints() instead, which returns a Bezier's control points
br.start, br.control1, br.control2, br.end = [3*mag + bpt for bpt in br.bpoints()]  #

tangent_line_r = svg.Line(br.point(t), br.point(t) + mag*br.unit_tangent(t))
normal_line_r = svg.Line(br.point(t), br.point(t) + mag*br.normal(t))
svg.wsvg([b, tangent_line, normal_line, br, tangent_line_r, normal_line_r],
     'bgpkgp', nodes=[b.point(t), br.point(t)], filename='svg_documentation_outputs/vectorframes.svg',
     text=["b's tangent", "br's tangent"], text_path=[tangent_line, tangent_line_r])

print("Seventh")
# Let's take a Line and an Arc and make some pictures
top_half = svg.Arc(start=-1, radius=1 + 2j, rotation=0, large_arc=1, sweep=1, end=1)
midline = svg.Line(-1.5, 1.5)

# First let's make our ellipse whole
bottom_half = top_half.rotated(180)
decorated_ellipse = svg.Path(top_half, bottom_half)

# Now let's add the decorations
for k in range(12):
    decorated_ellipse.append(midline.rotated(30 * k))

# Let's move it over so we can see the original Line and Arc object next
# to the final product
decorated_ellipse = decorated_ellipse.translated(4 + 0j)
svg.wsvg([top_half, midline, decorated_ellipse], filename='svg_documentation_outputs/decorated_ellipse.svg')

print("Eighth")
# First we'll load the path data from the file test.svg
paths, attributes = svg.svg2paths('bitmap_Layer 1_1.svg')

# Let's mark the parametric midpoint of each segment
# I say "parametric" midpoint because Bezier curves aren't
# parameterized by arclength
# If they're also the geometric midpoint, let's mark them
# purple and otherwise we'll mark the geometric midpoint green
min_depth = 5
error = 1e-4
dots = []
ncols = []
nradii = []
for path in paths:
    for seg in path:
        parametric_mid = seg.point(0.5)
        seg_length = seg.length()
        if seg.length(0.5)/seg.length() == 1/2:
            dots += [parametric_mid]
            ncols += ['purple']
            nradii += [5]
        else:
            t_mid = seg.ilength(seg_length/2)
            geo_mid = seg.point(t_mid)
            dots += [parametric_mid, geo_mid]
            ncols += ['red', 'green']
            nradii += [5] * 2

# In 'output2.svg' the paths will retain their original attributes
svg.wsvg(paths, nodes=dots, node_colors=ncols, node_radii=nradii,
     attributes=attributes, filename='svg_documentation_outputs/output2.svg')
