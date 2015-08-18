from collections import namedtuple
from math import sqrt
import random
import argparse
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from wand.display import display
import struct
import yaml
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color

try:
    import Image as Img
except ImportError:
    from PIL import Image as Img

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
    help="Path to image to extract colors")
ap.add_argument("-o", "--output", help="Filename to save image")
ap.add_argument("-p", "--palette", required=True,
    help="Color palette path (yaml)")
ap.add_argument("-c", "--colors", required=True,
    help="number of colors to extract")
args = vars(ap.parse_args())

width = 800
height = 600
color_width = 100
color_height = 60


Point = namedtuple('Point', ('coords', 'n', 'ct'))
Cluster = namedtuple('Cluster', ('points', 'center', 'n'))

def get_points(img):
    points = []
    w, h = img.size
    for count, color in img.getcolors(w * h):
        points.append(Point(color, 3, count))
    return points

rtoh = lambda rgb: '#%s' % ''.join(('%02x' % p for p in rgb))

def colorz(filename, n=3):
    img = Img.open(filename)
    img.thumbnail((200, 200))
    w, h = img.size

    points = get_points(img)
    clusters = kmeans(points, n, 1)
    rgbs = [map(int, c.center.coords) for c in clusters]
    return map(rtoh, rgbs)

def euclidean(p1, p2):
    return sqrt(sum([
        (p1.coords[i] - p2.coords[i]) ** 2 for i in range(p1.n)
    ]))

def calculate_center(points, n):
    vals = [0.0 for i in range(n)]
    plen = 0
    for p in points:
        plen += p.ct
        for i in range(n):
            vals[i] += (p.coords[i] * p.ct)
    return Point([(v / plen) for v in vals], n, 1)

def kmeans(points, k, min_diff):
    clusters = [Cluster([p], p, p.n) for p in random.sample(points, k)]

    while 1:
        plists = [[] for i in range(k)]

        for p in points:
            smallest_distance = float('Inf')
            for i in range(k):
                distance = euclidean(p, clusters[i].center)
                if distance < smallest_distance:
                    smallest_distance = distance
                    idx = i
            plists[idx].append(p)

        diff = 0
        for i in range(k):
            old = clusters[i]
            center = calculate_center(plists[i], old.n)
            new = Cluster(plists[i], center, old.n)
            clusters[i] = new
            diff = max(diff, euclidean(old.center, new.center))

        if diff < min_diff:
            break

    return clusters

def hex_to_lab(hx):
    rgb = sRGBColor.new_from_rgb_hex(hx)
    return convert_color(rgb, LabColor)

def closest_color(hx):
    if color_list.has_key(hx): return color_list[hx]
    distances = {}
    lab = hex_to_lab(hx)
    for key in color_list.keys():
        distances[key] = delta_e_cie2000(lab, hex_to_lab(key))
    return min(distances, key=distances.get)

color_list = yaml.load(open(args['palette'], 'r'))

exact_colors = colorz(args['image'], int(args['colors']))

colors = []
for color in exact_colors:
    colors.append(closest_color(color.replace('#', '')))


with Drawing() as draw:
    draw.stroke_color = Color("black")
    for i, color in enumerate(exact_colors):
        draw.fill_color = Color(color)
        draw.rectangle(left=width - (color_width * 2), top=color_height * i, width=color_width, height=color_height)

    for i, color in enumerate(colors):
        draw.fill_color = Color("#" + color)
        draw.rectangle(left=width - color_width, top=color_height * i, width=color_width, height=color_height)

    draw.fill_color = Color('black')
    draw.font_size = 18
    draw.text(width - (color_width * 2), color_height * len(colors) + 20, "Exact")
    draw.text(width - (color_width * 2) + color_width, color_height * len(colors) + 20, "Nearest")

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
