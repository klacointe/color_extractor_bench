from sklearn.cluster import KMeans
import argparse
import numpy as np
import cv2
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from wand.display import display
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
import yaml

def centroid_histogram(clt):
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins = numLabels)

    hist = hist.astype("float")
    hist /= hist.sum()

    return hist


def colorz(hist, centroids):
    c = []
    for (percent, color) in zip(hist, centroids):
        c.append({'color': color, 'percent': percent})
    return c

def hex_to_lab(hx):
    rgb = sRGBColor.new_from_rgb_hex(hx)
    return convert_color(rgb, LabColor)

def rgb_to_hex(r, g, b):
    return sRGBColor(r, g, b, is_upscaled=True).get_rgb_hex()

def closest_color(hx):
    if color_list.has_key(hx): return color_list[hx]
    distances = {}
    lab = hex_to_lab(hx)
    for key in color_list.keys():
        distances[key] = delta_e_cie2000(lab, hex_to_lab(key))
    return min(distances, key=distances.get)


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "Path to the image")
ap.add_argument("-c", "--clusters", required = True, type = int, help = "# of clusters")
ap.add_argument("-o", "--output", help="Filename to save image")
ap.add_argument("-p", "--palette", required=True, help="Color palette path (yaml)")
args = vars(ap.parse_args())

image = cv2.imread(args["image"])
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

image = image.reshape((image.shape[0] * image.shape[1], 3))

clt = KMeans(n_clusters = args["clusters"])
clt.fit(image)

hist = centroid_histogram(clt)
colors = colorz(hist, clt.cluster_centers_)

width = 800
height = 600
color_width = 100
color_height = 60

color_list = yaml.load(open(args['palette'], 'r'))

with Drawing() as draw:
    draw.stroke_color = Color("black")
    for i, color in enumerate(colors):
        near = closest_color(rgb_to_hex(color['color'][0], color['color'][1], color['color'][2]))
        exact = "rgb({0},{1},{2})".format(color['color'][0], color['color'][1], color['color'][2])
        draw.fill_color = Color(exact)
        draw.rectangle(left=(width - color_width * 2), top=color_height * i, width=color_width, height=color_height)
        draw.fill_color = Color("#" + near)
        draw.rectangle(left=width - color_width, top=color_height * i, width=color_width, height=color_height)
        t = "#" + near + " - %d%%" % int(color['percent'] * 100)
        draw.text(width - (color_width), (color_height * i) + (color_height / 2), t)

    with Image(width=width, height=height, background=Color('white')) as img:
        i = Image(filename=args['image'])
        i_width = width - (color_width * 2)
        i_height = i.height / (float(i.width) / i_width)
        draw.composite(operator='over', left=0, top=0, width=i_width, height=i_height, image=i)

        draw.draw(img)
        if args['output'] == None:
            display(img)
        else:
            img.save(filename=args['output'])
