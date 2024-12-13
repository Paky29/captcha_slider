import cv2
import os
from lxml import etree
import imgaug.augmenters as iaa
import imgaug as ia


def load_xml(xml_path):
    tree = etree.parse(xml_path)
    root = tree.getroot()
    coordinates = []
    for elem in root.findall('.//object/bndbox'):
        xmin = int(elem.find('xmin').text)
        ymin = int(elem.find('ymin').text)
        xmax = int(elem.find('xmax').text)
        ymax = int(elem.find('ymax').text)
        coordinates.append([xmin, ymin, xmax, ymax])
    return tree, root, coordinates


def save_xml(tree, root, new_coordinates, save_path, new_filename):
    for i, elem in enumerate(root.findall('.//object/bndbox')):
        elem.find('xmin').text = str(new_coordinates[i][0])
        elem.find('ymin').text = str(new_coordinates[i][1])
        elem.find('xmax').text = str(new_coordinates[i][2])
        elem.find('ymax').text = str(new_coordinates[i][3])

    root.find('filename').text = new_filename
    tree.write(save_path, pretty_print=True)


def apply_augmentations(image, coordinates, seq):
    bbs = ia.BoundingBoxesOnImage([
        ia.BoundingBox(x1=xmin, y1=ymin, x2=xmax, y2=ymax) for xmin, ymin, xmax, ymax in coordinates
    ], shape=image.shape)

    image_aug, bbs_aug = seq(image=image, bounding_boxes=bbs)
    new_coordinates = [[int(bb.x1), int(bb.y1), int(bb.x2), int(bb.y2)] for bb in bbs_aug.bounding_boxes]
    return image_aug, new_coordinates


def process_images_and_annotations(image_dir, xml_dir, save_image_dir, save_xml_dir, augmentations, num_augmentations):
    seq = iaa.Sequential(augmentations)

    for filename in os.listdir(image_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = image_dir+"/"+filename
            print(image_path)
            xml_path = os.path.join(xml_dir, filename.replace(".jpg", ".xml").replace(".png", ".xml"))
            image = cv2.imread(image_path)
            tree, root, coordinates = load_xml(xml_path)

            for i in range(num_augmentations):
                image_aug, new_coordinates = apply_augmentations(image, coordinates, seq)
                save_image_path = os.path.join(save_image_dir, f"augmented_{i}_" + filename)
                save_xml_path = os.path.join(save_xml_dir,
                                             f"augmented_{i}_" + filename.replace(".jpg", ".xml").replace(".png",
                                                                                                          ".xml"))
                cv2.imwrite(save_image_path, image_aug)
                save_xml(tree, root, new_coordinates, save_xml_path, f"augmented_{i}_" + filename)


# Augmentations to apply (keeping transformations minimal)
augmentations = [
    iaa.Fliplr(0.6),                                 # Always flip horizontally
    iaa.Flipud(0.6),                                 # Always flip vertically
    iaa.Affine(rotate=(-10, 10)),                    # Rotate between -10 and 10 degrees
    iaa.Affine(scale=(0.9, 1.1)),                    # Scale between 90% and 110%
    iaa.Affine(translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)}),  # Translate between -10% and 10% both horizontally and vertically
]

image_dir = "onion_img"
xml_dir = "coordinate"
save_image_dir = "onion_img"
save_xml_dir = "coordinate"

if __name__ == '__main__':
    # Ottieni tutti i percorsi delle immagini nella directory originale
    num_augmentations = 10
    process_images_and_annotations(image_dir, xml_dir, save_image_dir, save_xml_dir, augmentations, num_augmentations)