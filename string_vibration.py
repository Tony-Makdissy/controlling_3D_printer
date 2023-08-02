import cv2
import svgpathtools as svg
import numpy as np
import os
import cairosvg  # Import the cairosvg library for SVG to PNG conversion

output_dir = "string_vibration"
# check if a directory exists, if not create it
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

seg1 = svg.Line(0 + 100j, 0 + 0j)
seg2 = svg.Line(0 + 0j, 100 + 0j)
seg3 = svg.Line(100 + 0j, 100 + 100j)

changeable_seg = svg.QuadraticBezier(100 + 100j, 50 + 0j, 0 + 100j)
path = svg.Path(seg1, seg2, seg3, changeable_seg)

number_of_cycles = 5
frames_per_cycle = 10
# create a range of flaot numbers from 0 to number_of_cycles * 2pi with step 2pi/frames_per_cycle

# delete previous files
for file in os.listdir(output_dir):
    if file.endswith(".png") or file.endswith(".svg"):
        os.remove(os.path.join(output_dir, file))

# create a range of complex numbers
for i, theta in enumerate(np.linspace(0, number_of_cycles * 2 * np.pi, number_of_cycles * frames_per_cycle)):
    control_point = 50 + 100 * (1 + np.cos(theta)/2) * 1j

    path[-1] = svg.QuadraticBezier(0 + 100j, control_point, 100 + 100j)

    svg_file_path = f"{output_dir}/string_vibration_{i:05d}.svg"
    png_file_path = f"{output_dir}/string_vibration_{i:05d}.png"
    # https://blog.finxter.com/python-int-to-string-with-leading-zeros/


    # Save the SVG
    width = 150  # Width in pixels
    height = 250  # Height in pixels
    svg_attributes = {'width': width, 'height': height}
    attributes = [{'stroke': "#FFFFFF", 'stroke-width': 2, 'fill': "None"}]
    svg.wsvg(path, nodes=[control_point],
             node_colors=['purple'], node_radii=[5],
             filename=svg_file_path, attributes=attributes,
             svg_attributes=svg_attributes)
    # Convert the SVG to PNG
    cairosvg.svg2png(url=svg_file_path, write_to=png_file_path)

    # Delete the SVG
    # os.remove(svg_file_path)


# https://stackoverflow.com/a/44948030/15215520
image_folder = output_dir
video_name = 'video.avi'

images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
images.sort()
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

video = cv2.VideoWriter(video_name, 0, 1, (width, height))

for image in images:
    video.write(cv2.imread(os.path.join(image_folder, image)))

cv2.destroyAllWindows()
video.release()
