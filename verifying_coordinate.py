import os
import cv2
from lxml import etree


def load_xml_coordinates(xml_path):
    tree = etree.parse(xml_path)
    root = tree.getroot()
    coordinates = []
    for obj in root.findall('.//object'):
        xmin = int(obj.find('.//xmin').text)
        ymin = int(obj.find('.//ymin').text)
        xmax = int(obj.find('.//xmax').text)
        ymax = int(obj.find('.//ymax').text)
        coordinates.append((xmin, ymin, xmax, ymax))
    return coordinates


def crop_image(image, coordinates):
    cropped_images = []
    height, width = image.shape[:2]
    for (left, top, right, bottom) in coordinates:
        # Ensure the coordinates are within the image dimensions
        print(left, top, right, bottom)
        left = max(0, min(left, width - 1))
        top = max(0, min(top, height - 1))
        right = max(0, min(right, width))
        bottom = max(0, min(bottom, height))
        print(left, top, right, bottom)

        # Check if the coordinates form a valid rectangle
        if right > left and bottom > top:
            cropped_image = image[top:bottom, left:right]
            cropped_images.append(cropped_image)
        else:
            print(f"Invalid crop coordinates: ({left}, {top}, {right}, {bottom})")
    return cropped_images


def process_images_and_annotations(image_dir, xml_dir, save_dir):

    # Ensure the save directory exists
    os.makedirs(save_dir, exist_ok=True)

    # Loop through all files in the image directory
    for filename in os.listdir(image_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(image_dir, filename)
            xml_path = os.path.join(xml_dir, filename.replace(".jpg", ".xml").replace(".png", ".xml"))

            # Check if the XML file exists
            if not os.path.isfile(xml_path):
                print(f"XML file not found: {xml_path}")
                continue

            # Read the image
            image = cv2.imread(image_path)

            # Check if the image was successfully loaded
            if image is None:
                print(f"Failed to load image: {image_path}")
                continue

            # Load the coordinates from the XML file
            coordinates = load_xml_coordinates(xml_path)

            # Crop the image based on the coordinates
            cropped_images = crop_image(image, coordinates)

            # Save the cropped images
            for i, cropped_image in enumerate(cropped_images):
                if cropped_image.size == 0:
                    print(f"Cropped image is empty, skipping save for: {filename}_crop_{i}.png")
                    continue
                save_image_path = os.path.join(save_dir, f"{os.path.splitext(filename)[0]}_crop_{i}.png")
                cv2.imwrite(save_image_path, cropped_image)
                print(f"Cropped image saved: {save_image_path}")

# Directory paths
image_dir = 'onion_img'
xml_dir = 'coordinate'
save_dir = 'cropped_images'

if __name__ == '__main__':
    # Process all images and annotations
    process_images_and_annotations(image_dir, xml_dir, save_dir)
