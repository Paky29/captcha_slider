import numpy as np
import cv2
import os
from keras.preprocessing.image import ImageDataGenerator, img_to_array, array_to_img, load_img
import xml.etree.ElementTree as ET

# Directory delle immagini originali e annotate
original_data_dir = 'path_to_original_images'
annotated_data_dir = 'path_to_annotated_images'
augmented_data_dir = 'path_to_augmented_images'

# Creare il generatore di immagini per l'aumento dei dati
datagen = ImageDataGenerator(
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)


def adjust_coordinates(bbox, transform_matrix, img_shape):
    points = np.array([
        [bbox[0], bbox[1]],
        [bbox[2], bbox[1]],
        [bbox[2], bbox[3]],
        [bbox[0], bbox[3]]
    ])
    ones = np.ones(shape=(len(points), 1))
    points_ones = np.hstack([points, ones])
    transformed_points = transform_matrix.dot(points_ones.T).T
    transformed_points = transformed_points[:, :2]

    min_x = max(0, min(transformed_points[:, 0]))
    max_x = min(img_shape[1], max(transformed_points[:, 0]))
    min_y = max(0, min(transformed_points[:, 1]))
    max_y = min(img_shape[0], max(transformed_points[:, 1]))

    return [int(min_x), int(min_y), int(max_x), int(max_y)]


def augment_image(image_path, xml_path, save_dir):
    img = load_img(image_path)
    x = img_to_array(img)
    x = np.expand_dims(x, axis=0)

    img_shape = x.shape[1:3]

    tree = ET.parse(xml_path)
    root = tree.getroot()

    i = 0
    for batch in datagen.flow(x, batch_size=1):
        aug_img = array_to_img(batch[0])
        aug_img_path = os.path.join(save_dir, f"aug_{i}.jpg")
        aug_img.save(aug_img_path)

        aug_xml_path = os.path.join(save_dir, f"aug_{i}.xml")
        aug_tree = ET.ElementTree(ET.Element('annotation'))
        aug_root = aug_tree.getroot()

        for elem in root:
            aug_elem = ET.SubElement(aug_root, elem.tag)
            for subelem in elem:
                aug_subelem = ET.SubElement(aug_elem, subelem.tag)
                aug_subelem.text = subelem.text

        transform_matrix = datagen.get_random_transform(img_shape)
        transform_matrix = datagen.get_transformation_matrix(img_shape, transform_matrix)

        for obj in aug_root.findall('object'):
            bbox = obj.find('bndbox')
            xmin = int(bbox.find('xmin').text)
            ymin = int(bbox.find('ymin').text)
            xmax = int(bbox.find('xmax').text)
            ymax = int(bbox.find('ymax').text)
            new_bbox = adjust_coordinates([xmin, ymin, xmax, ymax], transform_matrix, img_shape)
            bbox.find('xmin').text = str(new_bbox[0])
            bbox.find('ymin').text = str(new_bbox[1])
            bbox.find('xmax').text = str(new_bbox[2])
            bbox.find('ymax').text = str(new_bbox[3])

        aug_tree.write(aug_xml_path)

        i += 1
        if i >= 20:
            break


for filename in os.listdir(original_data_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image_path = os.path.join(original_data_dir, filename)
        xml_path = os.path.join(annotated_data_dir, filename.replace(".jpg", ".xml").replace(".png", ".xml"))
        augment_image(image_path, xml_path, augmented_data_dir)
