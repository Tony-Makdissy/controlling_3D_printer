# Controlling the 3D printer

## Basic usage:
- Go to the file `main.py`, preferably with an IDE but any text editor will do.
- You can either define a circle or a square, or upload any svg file, I've included a few examples.
- In `fill` function: use `rotation` to rotate the filling lines, 0 will make them vertical, 90 will make them horizontal.
- In `fill` function: use `distance` to define the distance between the filling lines.
- Comment svg.dsvg(shapes) to get rid of the pop-up window, the pop-up window is to show you the shape and the filling lines.
- The first `commands.fast_movement()` call is to go to the correct position, change `z` or `speed` as you see fit.
- In the loop, change `commands.fast_movement()` to control how fast the printer go the beginning of each line.
- Change the paramters of `commands.inject_on_line()` to control the injection.
- Change the file name of wich the gcode will be saved to in `commands.save_gcode()`.
- Finally, run `main.py` and feed the gcode to the printer.

## Advanced usage:
I will try to comment the code in a way you can understand the code easily.
But I haven't done so for now!

## Printer model
KINGROON KP3S

Howver, the code should work with any printer that uses gcode (probably all of them!).

## References:
- https://howtomechatronics.com/tutorials/g-code-explained-list-of-most-important-g-code-commands/#:~:text=The%20G%2Dcode%20commands%20instruct,to%20get%20the%20desired%20shape.
- https://www.thomasnet.com/articles/custom-manufacturing-fabricating/g-code-commands/
- https://pypi.org/project/svgpathtools/
- https://github.com/mathandy/svgpathtools (same as previous, but more clear)
- https://css-tricks.com/svg-path-syntax-illustrated-guide/

