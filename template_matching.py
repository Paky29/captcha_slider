import datetime
from time import sleep
import cv2
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def find_subimage(path_image, path_subimage):
    path_image = "comp_img/comp.png"
    path_subimage = "sub_img/sub.png"

    # Load the large image and the subimage
    large_image = cv2.imread(path_image)
    sub_image = cv2.imread(path_subimage)

    # Convert images to grayscale
    large_image_gray = cv2.cvtColor(large_image, cv2.COLOR_BGR2GRAY)
    sub_image_gray = cv2.cvtColor(sub_image, cv2.COLOR_BGR2GRAY)

    # Perform template matching
    result = cv2.matchTemplate(large_image_gray, sub_image_gray, cv2.TM_CCOEFF_NORMED)

    # Get the coordinates of the best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Calculate the bottom-right corner of the rectangle
    h, w = sub_image_gray.shape
    bottom_right = (max_loc[0] + w, max_loc[1] + h)

    # Draw a rectangle around the matched region
    cv2.rectangle(large_image, max_loc, bottom_right, (0, 255, 0), 2)

    # Crop the matched region from the large image
    cropped_image = large_image[max_loc[1]:bottom_right[1], max_loc[0]:bottom_right[0]]

    # Display the result
    cv2.imshow('Detected Subimage', large_image)
    cv2.imshow('Cropped Image', cropped_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Coordinates of the top-left corner of the subimage in the large image
    print("Top-left corner:", max_loc)

    # Optionally, save the cropped image for further inspection
    cv2.imwrite('cropped_image.png', cropped_image)

    return min_val, max_val, min_loc, max_loc

def move_input(driver, path_image, path_subimage):
    # Load the large image and the subimage
    large_image = cv2.imread(path_image)
    sub_image = cv2.imread(path_subimage)

    # Convert images to grayscale
    large_image_gray = cv2.cvtColor(large_image, cv2.COLOR_BGR2GRAY)
    sub_image_gray = cv2.cvtColor(sub_image, cv2.COLOR_BGR2GRAY)

    # Perform template matching
    result = cv2.matchTemplate(large_image_gray, sub_image_gray, cv2.TM_CCOEFF_NORMED)

    # Get the coordinates of the best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Locate the slider element
    slider = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[name='cap_range']")))

    # Get the size of the slider element
    slider_size = slider.size
    slider_location = slider.location
    print(slider_location)
    slider_width = slider_size['height']

    # Assuming the slider range is known
    slider_min = int(slider.get_attribute('min'))
    slider_max = int(slider.get_attribute('max'))

    # Calculate the desired value based on the location of the subimage
    slider_value = (max_loc[0] / (large_image.shape[1] - sub_image.shape[1])) * (slider_max - slider_min) + slider_min
    slider_value = int(slider_value)

    #write the code to move the slider of 100 pixels using javscript to change the attribute value in the input field
    #driver.execute_script("arguments[0].setAttribute('value', arguments[1])", slider, slider_value)

    javascript_code = f"""
    document.querySelector('input[type="range"]').value = {slider_value};
    document.querySelector('input[type="range"]').dispatchEvent(new Event('input'));
    """

    driver.execute_script(javascript_code)
    sleep(5)


