import cv2
import numpy as np

# Load the image
image = cv2.imread('Binance BNB_USDT Liquidation Heatmap(24 hour)-2025-01-01_12_42_51.png')

# Get the width and height of the image
height, width, _ = image.shape

# Define the region to take (17.5% from the right side)
right_17_5_percent = int(width * 0.825)  # The first 82.5% of the image (excluding the right 17.5%)

# Crop the image to only include the rightmost 17.5%
cropped_image = image[:, right_17_5_percent:]

# Convert the cropped image to HSV color space for color detection
hsv_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)

# Visualize the original HSV image
cv2.imshow('HSV Image', hsv_image)
cv2.waitKey(0)  # This will let you see the HSV image
cv2.destroyAllWindows()

# Define the red color range (red has two ranges in HSV)
lower_red_1 = np.array([0, 120, 70])  # Lower range of red
upper_red_1 = np.array([10, 255, 255])  # Upper range of red

lower_red_2 = np.array([170, 120, 70])  # Lower range of red (other side of the hue spectrum)
upper_red_2 = np.array([180, 255, 255])  # Upper range of red

# Create masks for both red ranges
red_mask_1 = cv2.inRange(hsv_image, lower_red_1, upper_red_1)
red_mask_2 = cv2.inRange(hsv_image, lower_red_2, upper_red_2)

# Combine the red masks
red_mask = cv2.bitwise_or(red_mask_1, red_mask_2)

# Find contours in the red mask
red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Define the expanded yellow color range (yellow in HSV)
lower_yellow = np.array([20, 150, 150])  # Lower range of yellow (increased saturation and value)
upper_yellow = np.array([40, 255, 255])  # Upper range of yellow

# Create a yellow mask before filtering (to visualize if the yellow regions are detected)
yellow_mask_before_filtering = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

# Visualize the yellow mask before filtering to check if it captures yellow regions
cv2.imshow('Yellow Mask Before Filtering', yellow_mask_before_filtering)
cv2.waitKey(0)  # This will let you see the yellow regions detected
cv2.destroyAllWindows()

# Find contours in the yellow mask after filtering
yellow_contours, _ = cv2.findContours(yellow_mask_before_filtering, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# If red color is detected, process the contours
if len(red_contours) > 0:
    print("Red region detected in the image.")
    
    # Find the rightmost red contour (latest red color from the right side)
    rightmost_red_contour = max(red_contours, key=lambda c: cv2.boundingRect(c)[0])
    x, y, w, h = cv2.boundingRect(rightmost_red_contour)
    
    # Mark the rightmost red color with a circle (green)
    center = (x + w // 2, y + h // 2)
    cv2.circle(cropped_image, center, 10, (0, 255, 0), 2)  # Green circle for the latest red region

    # Initialize flags for detecting yellow regions
    yellow_above = False
    yellow_below = False
    
    # Define an offset for searching yellow regions to the left and right of the red region
    offset = 10000  # Move 500 pixels left and right from the red region

    # Loop through the yellow contours to check above and below the red region
    for yellow_contour in yellow_contours:
        x2, y2, w2, h2 = cv2.boundingRect(yellow_contour)
        yellow_center = (x2 + w2 // 2, y2 + h2 // 2)
        
        # Check for yellow regions within the red region's width (+ offset) and y-coordinate
        if (x - offset <= x2 + w2 // 2 <= x + w + offset):  # Yellow region's x-coordinate within the range
            if y2 + h2 <= y:  # Yellow is above the red region
                yellow_above = True
                # Mark the yellow region with a red circle
                cv2.circle(cropped_image, yellow_center, 10, (0, 0, 255), 2)  # Red circle for yellow region above
            elif y2 >= y + h:  # Yellow is below the red region
                yellow_below = True
                # Mark the yellow region with a red circle
                cv2.circle(cropped_image, yellow_center, 10, (0, 0, 255), 2)  # Red circle for yellow region below

    # Detect the rightmost yellow contour
    if len(yellow_contours) > 0:
        rightmost_yellow_contour = max(yellow_contours, key=lambda c: cv2.boundingRect(c)[0])
        x2, y2, w2, h2 = cv2.boundingRect(rightmost_yellow_contour)
        
        # Mark the rightmost yellow region with a blue circle
        yellow_center = (x2 + w2 // 2, y2 + h2 // 2)
        cv2.circle(cropped_image, yellow_center, 10, (255, 0, 0), 2)  # Blue circle for the rightmost yellow region
        print("Rightmost yellow region detected.")

    # Check if any yellow regions were detected and print a console message
    if yellow_above or yellow_below:
        print("Yellow regions detected.")
    
    # Determine the market sentiment based on yellow regions' position relative to red
    if yellow_above and yellow_below:
        print("Sideways market detected.")
    elif yellow_above:
        print("Bullish market detected.")
    elif yellow_below:
        print("Bearish market detected.")
    else:
        print("No clear sentiment.")

# Show the image with the detected regions
cv2.imshow('Detected Red and Yellow Regions', cropped_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save the output image with the marked regions
cv2.imwrite('output_image_with_yellow_and_red_marked_right_17_5_bright_yellow.png', cropped_image)
