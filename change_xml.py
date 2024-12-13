import xml.etree.ElementTree as ET
import os

from PIL import Image


def modify_filename_in_xml(file_path):
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Initialize variables to hold the original and new filenames
    original_filename = None
    new_filename = None

    # Iterate through elements to find the filename tag (assuming it's in a specific tag)
    for elem in root.iter():
        if 'name' in elem.attrib:
            original_filename = elem.attrib['name']
            # Find the position of the '-' character
            hyphen_index = original_filename.find('-')
            if hyphen_index != -1:
                # Remove characters up to and including the '-'
                new_filename = original_filename[hyphen_index + 1:]
                # Update the name attribute
                elem.set('name', new_filename)

    # Write the modified XML back to the file
    tree.write(file_path)

    # Rename the actual file if a new filename was determined
    if new_filename:
        # Get the directory of the original file
        directory = os.path.dirname(file_path)
        # Construct the full new file path
        new_file_path = os.path.join(directory, new_filename)
        # Rename the file
        os.rename(file_path, new_file_path)

    return new_file_path if new_filename else None

def remove_before_hyphen(input_string):
    # Find the position of the '-' character
    hyphen_index = input_string.find('-')
    if hyphen_index != -1:
        # Remove characters up to and including the '-'
        return input_string[hyphen_index + 1:]
    else:
        # If there's no '-' character, return the original string
        return input_string

def rename_file(current_file_path, new_file_name):
    # Get the directory of the current file
    directory = os.path.dirname(current_file_path)
    # Construct the full new file path
    new_file_path = os.path.join(directory, new_file_name)
    # Rename the file
    os.rename(current_file_path, new_file_path)
    return new_file_path

def modify_tag_value(file_path, new_value):
    dot_index = new_value.rfind('.')
    new_file_name = new_value[:dot_index] + ".png"

    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Find the tag and modify its value
    for elem in root.iter("filename"):
        elem.text = new_file_name

    # Write the modified XML back to the file
    tree.write(file_path)


def convert_image_format(input_path, output_path, output_format):
    # Open an image file
    with Image.open(input_path) as img:
        # Save the image in the new format
        img.save(output_path, format=output_format)

def batch_convert_images(input_dir, output_dir, output_format):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Loop through all files in the input directory
    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)

        # Check if the file is an image
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.' + output_format.lower())
            convert_image_format(input_path, output_path, output_format)

# Example usage
input_directory = 'onion_img'
output_directory = 'onion_img'
output_format = 'PNG'

if __name__ == '__main__':
    #batch_convert_images(input_directory, output_directory, output_format)

    for filename in os.listdir("coordinate"):
        new_file_name = remove_before_hyphen(filename)
        new_path = rename_file("coordinate/"+filename, new_file_name)
        modify_tag_value(new_path, new_file_name)
