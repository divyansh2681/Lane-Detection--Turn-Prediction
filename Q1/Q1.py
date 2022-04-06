# -*- coding: utf-8 -*-
"""q1_histogram_iter1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-wPkzYIMPjqilyzaoZ0OibPpGUU2iZoY
"""

import numpy as np
import glob
import cv2

def creating_histogram(image, bins):
    
    # array with size of bins, set to zeros
    histogram = np.zeros(bins)
    
    # loop through pixels and sum up counts of pixels
    for pixel in image:
        histogram[pixel] += 1
    
    # return our final result
    return histogram

# create our cumulative sum function
def cumulative(a):

    b = []
    j = 0
    for i in range(0, len(a)):
        j = j + a[i]
        b.append(j)

    return np.array(b)

def histogram_equ(img):


    img = np.asarray(img)

    # put pixels in a 1D array by flattening out img array
    flat = img.flatten()

    # execute our histogram function
    hist = creating_histogram(flat, 256)

    # execute the cumulative function
    cs = cumulative(hist)

    # re-normalize the cumsum
    nj = (cs - cs.min()) * 255
    N = cs.max() - cs.min()
    cs = nj / N

    # convert it back to uint8 since we can't use floating point values in images
    cs = cs.astype('uint8')
    
    # get the value from cumulative sum for every index in flat, and set that as img_new
    img_new = cs[flat]

    # put array back into original shape since we flattened it
    img_new = np.reshape(img_new, img.shape)

    return img_new

framess = []
framess = [cv2.imread(img) for img in glob.glob('Q1/*.png')] # glob.glob is used here to access all images present in a folder

### SIMPLE HISTOGRAM EQUALIZATION ####

size = (framess[0].shape[1], framess[0].shape[0])
Vid = cv2.VideoWriter('simple_hist_eq.avi',cv2.VideoWriter_fourcc(*'DIVX'), 10, size)
for img_simple_hist_eq in framess:

    img_new = histogram_equ(img_simple_hist_eq)
    Vid.write(img_new)

    # cv2.imshow('hist_eq', img_new)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

#### ADAPTIVE HISTOGRAM EQUALIZATION ####

size = (framess[0].shape[1], framess[0].shape[0])
Vid = cv2.VideoWriter('adaptive_hist_eq.avi',cv2.VideoWriter_fourcc(*'DIVX'), 8, size)


for img_adaptive_hist_eq in framess:
    # img_adaptive_hist_eq = cv2.imread(img)
    test_image = np.array(img_adaptive_hist_eq)
    
    # Define the window size
    windowsize_rows = 100
    windowsize_cols = 100

    # Crop out the window and calculate the histogram
    copy_img = test_image.copy()
    for r in range(0,test_image.shape[0], windowsize_rows):
        for c in range(0,test_image.shape[1] , windowsize_cols):
            window = test_image[r:r+windowsize_rows,c:c+windowsize_cols]
            new_img = histogram_equ(window) ## running histogram equalization on each window
            test_image[r:r+windowsize_rows,c:c+windowsize_cols] = new_img ## updating the original image copy with the new image

    Vid.write(test_image)

        # cv2.imshow('adaptive_hist_eq', test_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()