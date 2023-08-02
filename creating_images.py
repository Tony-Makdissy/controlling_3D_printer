import matplotlib.pyplot as plt
import numpy as np
import os

path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)

Directory_Name = "files-generated"
try:
    # Create the directory
    os.mkdir(Directory_Name)
    print("Directory", Directory_Name, "Created.")
except FileExistsError:
    # If the directory already exists
    print("Saving in", Directory_Name, "directory.")

path += "/" + Directory_Name
os.chdir(path)

# Circle
circle = True  # True or False
R = 8  # in mm

# nubmber of drops (ignore if circle = True)
nbX = 5
nbY = 5

# number of layers
nbZ = 2

spacing = 1.75  # in mm
T = 500  # in ms

# Initial position
X0 = 90
Y0 = 90

# capillary heights
Zoutliq = 17  # in mm
Zinliq = 13  # in mm

directionX = 1
directionY = 1
directionSpir = -1  # (if it's circle) -1 to start from the center and 1 to start from the edge
# TODO: check if this is correct

X = X0
Y = Y0

plotX = []
plotY = []
drops_per_layer = [0]

gcode = "G1 Z40 F1000 ; Move to start position\n"
gcode += "G1 X" + str(round(X, 1)) + " Y" + str(round(Y, 1)) + " Z40 F5000 ; Move to start position\n\n"
gcode += "G1 Z" + str(round(Zoutliq, 1)) + " F5000 ; \n\n\n"

if circle:
    # centre of the circle
    Xc = X0
    Yc = Y0 + R

    nbX = int(2 * R / spacing + 1)
    nbY = int(2 * R / (3 * spacing ** 2 / 4) ** 0.5 + 1)

    for k in range(nbZ):
        # start point of the mesh
        X = Xc - (nbX - 1) * spacing / 2
        Y = Yc - (nbY - 1) * (3 * spacing ** 2 / 4) ** 0.5 / 2

        if k != 0:
            gcode += "G4 P250; new layer\n\n"
            if k % 2 != 0:
                # TODO: not sure if this is "if" needs indentation
                X += spacing / 2

        plot = [(X, Y)]  # list intilization

        if len(plot) == 1:
            while (X - Xc) ** 2 + (Y - Yc) ** 2 > R ** 2:  # first drop
                X += spacing
            plot.append((X, Y))

        n = 0  # number of possiblities that a drop is already done or it's outside the circle TODO: check if this is correct
        while n < 6:
            # save in 'r' the vector between two previous drops
            r = plot[-1][0] - plot[-2][0] + 1j * (plot[-1][1] - plot[-2][1])
            theta = np.angle(r)

            # We're gonna test all pi/3 angles until we find a convenient postion and start from the following one
            thetaNew = theta - 2 / 3 * np.pi
            rNew = spacing * np.exp(1j * thetaNew)
            X = plot[-1][0] + rNew.real
            Y = plot[-1][1] + rNew.imag

            n = 1

            while ((X - Xc) ** 2 + (Y - Yc) ** 2 > R ** 2 or (
                    (X, Y) in plot)) and n < 6:  # if the drop is outside the circle or it's already done
                thetaNew += np.pi / 3
                rNew = spacing * np.exp(1j * thetaNew)
                X = plot[-1][0] + rNew.real
                Y = plot[-1][1] + rNew.imag
                n += 1

            if n < 6:
                # for not taking into account the final step where all the neighbours are already done
                plot.append((X, Y))

        plot.pop(0)  # earsing the first element of the list

        drops_per_layer.append(len(plot) + drops_per_layer[-1])  # to count the number of drops of this layer

        if directionSpir == -1:
            plot.reverse()
        for Xi, Yi in plot:  # print the gcode for the current layer with three decimals
            gcode += "G1 X%.3f Y%.3f F1000 ; \n\n" % (Xi, Yi)  # doing new droplet
            gcode += "G4 Z" + str(round(Zinliq, 1)) + " F5000 ; a drop\nG4 P" + str(T) + \
                     ";\nG1 Z" + str(round(Zoutliq, 1)) + " F5000 ; \n\n"
            plotX.append(Xi)
            plotY.append(Yi)

        directionSpir *= -1  # to change the direction of the spiral

    if nbZ != 1:
        name = "R%g_spacing%g_x%g_%gdrops" % (R, spacing, nbZ, len(plotX))
    else:
        name = "R%g_spacing%g_%gdrops" % (R, spacing, len(plotX))

else:
    plotX.append(X)
    plotY.append(Y)

    for k in range(nbZ):
        if k != 0:
            gcode += "G4 P250; new layer\n"
            X += directionX * spacing / 2
            gcode += "G1 X%.3f Y%.3f F1000 ; \n\n" % (X, Y)

        for i in range(nbY):
            if i != 0:
                X += directionX * spacing / 2
                Y += directionY * (3 * spacing ** 2 / 4) ** 0.5
                gcode += "G1 X%.3f Y%.3f F1000 ; new line\n\n" % (X, Y)

            for j in range(nbX):
                if j != 0:
                    X += directionX * spacing
                    gcode += "G1 X%.3f Y%.3f F1000 ; \n\n" % (X, Y)

                # new droplet
                gcode += "G1 Z" + str(round(Zinliq, 1)) + " F5000 ; a droplete \nG4 P" + str(T) + ";\nG1 Z" + str(
                    round(Zoutliq, 1)) + " F5000 ; \n\n"

                plotX.append(X)
                plotY.append(Y)

            directionX *= -1  # to change the direction at the end of the line
        directionY *= -1
        drops_per_layer.append(len(plotX) - 1)  # to count the number of drops of this layer
    plotY.pop(0)  # to erase the first element of the list
    plotX.pop(0)

    if nbZ != 1:
        name = str(nbX) + "x" + str(nbY) + "x" + str(nbZ) + "_spacing" + str(spacing)
    else:
        name = str(nbX) + "x" + str(nbY) + "_spacing" + str(spacing)

gcode += "\nG1 Z40.0 F5000; Move Z axis up little to prevent scratching\n"
gcode += "G1 X90 Y10 Z40.0 F1000; Moving back to prepration position\n"
gcode += "G1 Z40.0 F1000; Moving back to prepration position\n"*2

drops_per_layer.pop(0)  # to erase the first element of the list

print("\n%g droplets over %g layer(s), is around %g droplets per layer" % (len(plotX), nbZ, len(plotX) / nbZ))

print("saving in '%s' file. \n" % name)
file = open(name + ".gcode", "w")
file.write(gcode)
file.close()

title = name

fig = plt.figure(title, frameon=False)
ax = fig.add_subplot(1, 1, 1)

plt.plot(plotX[:drops_per_layer[0]], plotY[:drops_per_layer[0]], 'o-', label="layer 1")

if nbZ > 1:
    plt.plot(plotX[drops_per_layer[0]:drops_per_layer[1]], plotY[drops_per_layer[0]:drops_per_layer[1]], 'o-m', label="layer 2")
if nbZ > 2:
    plt.plot(plotX[drops_per_layer[1]:drops_per_layer[2]], plotY[drops_per_layer[1]:drops_per_layer[2]], 'p--', label="layer 3")
if nbZ > 3:
    plt.plot(plotX[drops_per_layer[2]:drops_per_layer[3]], plotY[drops_per_layer[2]:drops_per_layer[3]], '*--', label="layer 4")

plt.legend()
plt.plot(X0, Y0, "+r")

if circle:
    plt.plot(Xc, Yc, "+g")
    ax.add_patch(plt.Circle((Xc, Yc), R, color='c', alpha=0.2))
    plt.text(X0+spacing/10, Y0, r"($X_0, Y_0$)", verticalalignment='center', horizontalalignment='left')
else:
    plt.text(X0+spacing/10, Y0+spacing/10, r"($X_0, Y_0$)", verticalalignment='bottom', horizontalalignment='left')

plt.title(title)
ax.axis('equal')

plt.minorticks_on()
plt.grid(which='major')
plt.grid(which='minor', alpha=0.2, linestyle='--')

plt.show()


# # read the gcode file and add N%g at the beginning of each line
# file = open(name + ".gcode", "r")
# # go line by line and add N%g at the beginning of each line
# gcode = ""
# N = 1
# for line in file:
#     line.strip()
#     if line == "\n": continue
#     # find the semi-colon and remove everything after it
#     if ";" in line:
#         line = line[:line.find(";") + 1]
#     # gcode += "N%g " % N + line + "\n"
#     gcode += line + "\n"
#
#     N += 1
# file.close()
#
# file = open(name + ".gcode", "w")
# file.write(gcode)
# file.close()