# -*- coding: utf-8 -*-
"""q3_turn_detection_iteration_2_final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1G9UEMKSeJnZE4IylXjJt7K4Tcqz1I2tP
"""

import numpy as np
import matplotlib.pyplot as plt
import cv2

# Source points for homography
src = np.array([[200,675],[1150,675],[775,450],[550,450]], dtype="float32")               

# Destination points for homography
window_w = 600
window_h = 300
dst = np.array([[0, window_h], [window_w, window_h], [window_w, 0], [0,0]], dtype="float32")

# Homography 
H_matrix, __  = cv2.findHomography(src, dst)              
Hinv = np.linalg.inv(H_matrix)

def image_cropping(img, vertices):
    # Define a blank matrix that matches the image height/width.
    mask = np.zeros_like(img)    
    black = (255,255,255)
    # Fill inside the polygon
    cv2.fillPoly(mask, vertices, black)
    # Returning the image only where mask pixels match
    masked_img = cv2.bitwise_and(mask, img)
    return masked_img

def predict_turn(a, b):
    if b > a:
        return 'Right'
    elif b < a:
        return 'Left'
    else:
        return 'Straight'

# function to calculate slope of a line given end points of the line
def lineSlope(x1,y1,x2,y2):
    slope = float((y2-y1)/(x2-x1))
    return slope

# function resizes the frame and maintains the aspect ratio [source given in the reference section of the report]

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def masking_lanes(frame):

    hsl_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS) # converting the image to HSL
    yellow_low = np.array([20, 120, 80], dtype='uint8')
    yellow_high = np.array([45, 200, 255], dtype='uint8')        
    yellow = cv2.inRange(hsl_img, yellow_low, yellow_high)
    yellow_lane_only = cv2.bitwise_and(hsl_img, hsl_img, mask= yellow).astype(np.uint8)

	# To seperate out White colored lanes
    white_low = np.array([0, 200, 0], dtype='uint8')
    white_high = np.array([255, 255, 255], dtype='uint8')
    white = cv2.inRange(hsl_img, white_low, white_high)
    white_lane_only = cv2.bitwise_and(hsl_img, hsl_img, mask= white).astype(np.uint8)

	# Combine both
    both_lanes_hsl = cv2.bitwise_or(yellow_lane_only, white_lane_only)

    ##### converting to grayscale for single channel
    both_lanes_bgr = cv2.cvtColor(both_lanes_hsl, cv2.COLOR_HLS2BGR)
    both_lanes_gray = cv2.cvtColor(both_lanes_bgr, cv2.COLOR_BGR2GRAY)

    return both_lanes_hsl, both_lanes_bgr, both_lanes_gray

def lane_segregation(warped_img_color, lines):

    for i in range(len(lines)):
      for x1,y1,x2,y2 in lines[i]:
        cv2.line(warped_img_color, (x1, y1), (x2,y2), (0,0,255), 5)
        
    coordinates = []

    for i in range(len(lines)):

        coordinates.append([lines[i][0][0], lines[i][0][1]])
        coordinates.append([lines[i][0][2], lines[i][0][3]])

    coordinates = sorted(coordinates , key=lambda k: [k[1], k[0]], reverse=True)

    coordinates_left_lane = []
    coordinates_right_lane = []

    for i in range(len(coordinates)):
        if coordinates[i][0] < 200: # this 300 is from warped_img_color and not from out
            coordinates_left_lane.append(coordinates[i])
        elif coordinates[i][0] > 400:
            coordinates_right_lane.append(coordinates[i])
        else:
            pass


    coordinates_left_lane = sorted(coordinates_left_lane , key=lambda k: [k[1], k[0]], reverse=True)
    coordinates_right_lane = sorted(coordinates_right_lane , key=lambda k: [k[1], k[0]], reverse=True)


    ####### FOR LEFT LANE ######
    left_list_x_coord = []
    left_list_y_coord = []
            
    for i in range(len(coordinates_left_lane)):
        left_list_x_coord.append(coordinates_left_lane[i][0])
        left_list_y_coord.append(coordinates_left_lane[i][1])

    left_list_x_coord=np.array(left_list_x_coord)
    left_list_y_coord=np.array(left_list_y_coord)

    fit = np.polyfit(left_list_x_coord, left_list_y_coord, 2)
    a = fit[0]
    b = fit[1]
    c = fit[2]

    test = range(0, 120)
    test = np.array(test)
    left_plot_yy = []

    for i in range(len(test)):
        yy = a * np.square(test[i]) + b * test[i] + c
        left_plot_yy.append(yy)

    for i in range(0, len(left_plot_yy)-2):              
        cv2.line(warped_img_color, (test[i], np.uint16(left_plot_yy[i])), (test[i+1], np.uint16(left_plot_yy[i+1])), (0,255,0), 20)
        line_slope_1 = lineSlope(test[i], (left_plot_yy[i]), test[i+1],(left_plot_yy[i+1]))
        line_slope_2 = lineSlope(test[i+1], (left_plot_yy[i+1]), test[i+2],(left_plot_yy[i+2]))                    

        turn = predict_turn(line_slope_1, line_slope_2)  # calling the turn prediction function
        

    ym_per_pix = 3.048/100 # meters per pixel in y dimension, lane line is 10 ft = 3.048 meters (standard data)
    xm_per_pix = 3.7/378

    curve_radius_left = ((1 + (2*fit[0]*300*ym_per_pix + fit[1])**2)**1.5) / np.absolute(2*fit[0])   ## 300 is the window height          


    ####### FOR RIGHT LANE ########

    right_list_x_coord = []             
    right_list_y_coord = []

    for i in range(len(coordinates_right_lane)):
        right_list_x_coord.append(coordinates_right_lane[i][0])
        right_list_y_coord.append(coordinates_right_lane[i][1])          

    right_list_x_coord=np.array(right_list_x_coord)
    right_list_y_coord=np.array(right_list_y_coord)

    fit_right = np.polyfit(right_list_x_coord, right_list_y_coord, 2)
    a_right = fit_right[0]
    b_right = fit_right[1]
    c_right = fit_right[2]

    right_plot_yy = []

    test_right = range(480,580)  
    test_right = np.array(test_right)

    for i in range(len(test_right)):
        
        yy_right = a_right * np.square(test_right[i]) + b_right * test_right[i] + c_right            
        right_plot_yy.append(yy_right)
        
    for i in range(0, len(right_plot_yy)-1):
        cv2.line(warped_img_color, (test_right[i], np.uint16(right_plot_yy[i])), (test_right[i+1], np.uint16(right_plot_yy[i+1])), (0,255,0), 10)   
    
    points_for_fillpoly = np.array([[test[0], left_plot_yy[0]], [test_right[-1], right_plot_yy[-1]], [test_right[0], right_plot_yy[0]], [test[-1], left_plot_yy[-1]]])

    warped_img_color_copy = warped_img_color.copy()
    
    cv2.fillPoly(warped_img_color, pts = np.int32([points_for_fillpoly]), color = (0,255,0)) # creating a polygon infront of the car

    return warped_img_color_copy, warped_img_color, turn, curve_radius_left

cap = cv2.VideoCapture('challenge.mp4')
out_vid = cv2.VideoWriter('Q3_turn_detection_vid.avi',cv2.VideoWriter_fourcc(*'MJPG'), 20, (1829,500))            


if (cap.isOpened()== False): 
  print("Error opening video stream or file")

while(cap.isOpened()):   
 
  ret, frame = cap.read()
  if ret == True:

    height, width, __ = frame.shape

    both_lanes_hsl, both_lanes_bgr, both_lanes_gray = masking_lanes(frame)

    region_of_interest = [(300,675), (1130,675), (700,425), (620,425)]

             
    img_edge = cv2.Canny(both_lanes_gray,50,150) # canny edge detection
    cropped_img = image_cropping(img_edge, np.array([region_of_interest], np.int32)) # cropping the image using region of interest
    warped_img = cv2.warpPerspective(cropped_img, H_matrix, (window_w,window_h)) # warping the cropped grayscale image 
    warped_img_color = cv2.warpPerspective(frame, H_matrix, (window_w,window_h)) # warping the coloured image      

                            

    rho = 2  # parameters for hough transform                           
    theta = np.pi/180   
    thresh = 10                       
    minLineLength = 5                                                    
    maxLineGap = 5                                           
    lines = cv2.HoughLinesP( warped_img, rho, theta, thresh, np.array([]), minLineLength, maxLineGap) 

    warped_img_color_copy, warped_img_color, turn, curve_radius_left = lane_segregation(warped_img_color, lines)
              
    new_out_img = np.zeros_like(frame.shape)
    new_out_img = cv2.warpPerspective(warped_img_color, np.linalg.inv(H_matrix), (width,height)) # unwarping the warped image
    out = cv2.bitwise_or(frame, new_out_img) # bitwise_or of the unwarped image and the initial frame so that features of unwarped image come on initial frame

    font = cv2.FONT_HERSHEY_TRIPLEX             
    cv2.putText(out, str('Average Curvature: ' + str(curve_radius_left) + 'm'), (50,50), font, 1, (0,255,255),2,cv2.LINE_4)
    cv2.putText(out, str('Turn ' + str(turn)), (50,100), font, 1, (0,255,255),2,cv2.LINE_4)

    ########## FOR MAKING THE VIDEO, STACKING AND RESIZING THE FRAMES #######
    

    img1 = frame

    img2 = both_lanes_bgr
    
    img3 = np.zeros_like(warped_img_color) # converting single channel image into 3 channel
    img3[:,:,0] = warped_img
    img3[:,:,1] = warped_img
    img3[:,:,2] = warped_img

    img4 = warped_img_color_copy   

    img5 = out

    img1 = image_resize(img1, height=300) # resizing
    cv2.putText(img1, str('Undistorted'), (50,50), font, 1, (0,255,255),2,cv2.LINE_4)
    img2 = image_resize(img2, height=300)
    cv2.putText(img2, str('Lane Color Detection'), (50,50), font, 1, (0,255,255),2,cv2.LINE_4)
    img3 = image_resize(img3, height=300)
    cv2.putText(img3, str('Warped'), (50,50), font, 1, (0,255,255),2,cv2.LINE_4)
    img4 = image_resize(img4, height=300)
    cv2.putText(img4, str('Curve Fitting'), (50,50), font, 1, (0,255,255),2,cv2.LINE_4)

    hstack_1_2 = np.hstack((img1, img2)) # stacking
    hstack_3_4 = np.hstack((img3, img4))
    
    hstack_1_2 = image_resize(hstack_1_2, width=800)
    hstack_3_4 = image_resize(hstack_3_4, width=800)  

    all_4 = np.vstack((hstack_1_2, hstack_3_4))
    all_4 = image_resize(all_4, height=500)

    img5 = image_resize(img5, height=500)

    total = np.hstack((img5, all_4))
    # out_vid.write(total)                            

    cv2.imshow('Frame', total)       
    if cv2.waitKey(0) & 0xFF == ord('q'):
      break

  else: 
    break            
                
out_vid.release()
cap.release()

cv2.destroyAllWindows()
