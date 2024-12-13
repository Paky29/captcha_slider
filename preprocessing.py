import os
import cv2
import numpy as np

def preprocess_images(input_dir, output_dir, image_size=(128, 128)):
    # Crea la cartella di output se non esiste
    os.makedirs(output_dir, exist_ok=True)

    # Lista di tutti i file nella cartella di input
    input_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]

    # Preprocessing di ciascuna immagine e salvataggio nella cartella di output
    for file_name in input_files:
        # Carica l'immagine
        image_path = os.path.join(input_dir, file_name)
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)

        # Normalizza i valori dei pixel tra [0, 1]
        normalized_image = image / 255.0

        # Rimozione del rumore usando GaussianBlur
        denoised_image = cv2.GaussianBlur(normalized_image, (5, 5), 0)

        # Converti l'immagine denoised a valori [0, 255] per il salvataggio
        denoised_image_uint8 = np.uint8(denoised_image * 255)

        # Salva l'immagine preprocessata
        output_path = os.path.join(output_dir, file_name)
        cv2.imwrite(output_path, denoised_image_uint8)

# Esempio di utilizzo:
input_dir = 'onion_img'  # Sostituisci con il percorso della cartella di input
output_dir = 'preprocessing_image'  # Sostituisci con il percorso della cartella di output

if __name__ == '__main__':
    preprocess_images(input_dir, output_dir)