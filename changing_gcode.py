# read KKP3_10.gcode file and devide all the F values by 2 until you finde z1 and then stop
name = "KKP3_10y"
file = open(name + ".gcode", "r")

cnt = 0
for line in file:
    print(line)
    cnt += 1
    if cnt == 10:
        break