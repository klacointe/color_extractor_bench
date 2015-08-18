import cv2
from scipy.cluster.vq import vq, kmeans
from matplotlib import pyplot as plt
import numpy as np
import time as t
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
    help="Path to image to extract colors")
args = vars(ap.parse_args())

target_image = args["image"]

img = cv2.imread(target_image)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

hsv_image = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

def do_cluster(hsv_image, K, channels):
    # gets height, width and the number of channes from the image shape
    h,w,c = hsv_image.shape
    # prepares data for clustering by reshaping the image matrix into a (h*w) x c matrix of pixels
    cluster_data = hsv_image.reshape( (h*w,c) )
    # grabs the initial time
    t0 = t.time()
    # performs clustering
    codebook, distortion = kmeans(np.array(cluster_data[:,0:channels], dtype=np.float), K)
    # takes the final time
    t1 = t.time()
    print "Clusterization took %0.5f seconds" % (t1-t0)

    # calculates the total amount of pixels
    tot_pixels = h*w
    # generates clusters
    data, dist = vq(cluster_data[:,0:channels], codebook)
    # calculates the number of elements for each cluster
    weights = [len(data[data == i]) for i in range(0,K)]

    # creates a 4 column matrix in which the first element is the weight and the other three
    # represent the h, s and v values for each cluster
    color_rank = np.column_stack((weights, codebook))
    # sorts by cluster weight
    color_rank = color_rank[np.argsort(color_rank[:,0])]

    # creates a new blank image
    new_image =  np.array([0,0,255], dtype=np.uint8) * np.ones( (500, 500, 3), dtype=np.uint8)
    img_height = new_image.shape[0]
    img_width  = new_image.shape[1]

    # for each cluster
    for i,c in enumerate(color_rank[::-1]):

        # gets the weight of the cluster
        weight = c[0]

        # calculates the height and width of the bins
        height = int(weight/float(tot_pixels) *img_height )
        width = img_width/len(color_rank)

        # calculates the position of the bin
        x_pos = i*width



        # defines a color so that if less than three channels have been used
        # for clustering, the color has average saturation and luminosity value
        color = np.array( [0,128,200], dtype=np.uint8)

        # substitutes the known HSV components in the default color
        for j in range(len(c[1:])):
            color[j] = c[j+1]

        # draws the bin to the image
        new_image[ img_height-height:img_height, x_pos:x_pos+width] = [color[0], color[1], color[2]]

    # returns the cluster representation
    return new_image

# creates a new figure size 12x10 inches
plt.figure(figsize=(12,10))
# creates a 4-column subplot
plt.subplot(141)
# in the first cell draws the target image
plt.imshow(img)

for i in range(1,4):
    plt.subplot(141 + i)
    plt.title("Channels: %i" % i)
    new_image = do_cluster(hsv_image, 5, i)
    new_image = cv2.cvtColor(new_image, cv2.COLOR_HSV2RGB)
    plt.imshow(new_image)

plt.show()
