import tensorflow as tf
import matplotlib.pyplot as plt
from keras import layers
import numpy as np
import os
import time
from PIL import Image
from keras.src.saving import load_model


def make_generator_model():
    model = tf.keras.Sequential([
        layers.Dense(128 * 15 * 10, activation="relu", input_dim=100),
        layers.Reshape((15, 10, 128)),

        layers.Conv2DTranspose(128, kernel_size=(3, 3), strides=(1, 1), padding="same", activation="relu"),
        layers.BatchNormalization(),

        layers.Conv2DTranspose(64, kernel_size=(3, 3), strides=(2, 1), padding="same", activation="relu"),
        layers.BatchNormalization(),

        layers.Conv2DTranspose(32, kernel_size=(3, 3), strides=(3, 5), padding="same", activation="relu"),
        layers.BatchNormalization(),

        layers.Conv2DTranspose(3, kernel_size=(3, 3), strides=(4, 5), padding="same", activation="tanh"),
        layers.BatchNormalization()


    ])
    return model


# Creazione del modello del Discriminatore
def make_discriminator_model():
    model = tf.keras.Sequential([
    layers.Input(shape=(360, 250, 3)),
    layers.Conv2D(64, kernel_size=4, strides=2, padding="same"),
    layers.LeakyReLU(negative_slope=0.2),

    layers.Conv2D(128, kernel_size=4, strides=2, padding="same"),
    layers.LeakyReLU(negative_slope=0.2),
    layers.BatchNormalization(),

    layers.Conv2D(256, kernel_size = 4, strides = 2, padding = "same"),
    layers.LeakyReLU(negative_slope=0.2),
    layers.BatchNormalization(),

    layers.Conv2D(512, kernel_size = 4, strides = 2, padding = "same"),
    layers.LeakyReLU(negative_slope=0.2),
    layers.BatchNormalization(),

    layers.Flatten(),
    layers.Dense(1, activation='sigmoid')
    ])
    return model


# Funzioni di perdita e ottimizzatori
cross_entropy = tf.keras.losses.BinaryCrossentropy(from_logits=True)


def discriminator_loss(real_output, fake_output):
    real_loss = cross_entropy(tf.ones_like(real_output), real_output)
    fake_loss = cross_entropy(tf.zeros_like(fake_output), fake_output)
    total_loss = real_loss + fake_loss
    return total_loss


def generator_loss(fake_output):
    return cross_entropy(tf.ones_like(fake_output), fake_output)


generator = make_generator_model()
discriminator = make_discriminator_model()

generator_optimizer = tf.keras.optimizers.Adam(1e-4)
discriminator_optimizer = tf.keras.optimizers.Adam(1e-4)

# Definizione del ciclo di training
EPOCHS = 50
noise_dim = 100
num_examples_to_generate = 16

# Seme fisso per la generazione di immagini
seed = tf.random.normal([num_examples_to_generate, noise_dim])


@tf.function
def train_step(images):
    noise = tf.random.normal([32, noise_dim])

    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
        generated_images = generator(noise, training=True)
        real_output = discriminator(images, training=True)
        fake_output = discriminator(generated_images, training=True)

        gen_loss = generator_loss(fake_output)
        disc_loss = discriminator_loss(real_output, fake_output)

    gradients_of_generator = gen_tape.gradient(gen_loss, generator.trainable_variables)
    gradients_of_discriminator = disc_tape.gradient(disc_loss, discriminator.trainable_variables)

    generator_optimizer.apply_gradients(zip(gradients_of_generator, generator.trainable_variables))
    discriminator_optimizer.apply_gradients(zip(gradients_of_discriminator, discriminator.trainable_variables))


def train():
    image_dir = "onion_img"

    # Creazione di una lista di tutti i percorsi delle immagini nella cartella
    image_paths = [os.path.join(image_dir, filename) for filename in os.listdir(image_dir) if
                   filename.endswith('.jpg') or filename.endswith('.png')]

    # Creazione del dataset TensorFlow
    train_dataset = tf.data.Dataset.from_tensor_slices(image_paths)
    train_dataset = train_dataset.map(load_and_preprocess_image, num_parallel_calls=tf.data.experimental.AUTOTUNE)
    train_dataset = train_dataset.shuffle(buffer_size=len(image_paths)).batch(
        32)  # Modifica il batch size se necessario
    train_dataset = train_dataset.prefetch(buffer_size=tf.data.experimental.AUTOTUNE)

    for epoch in range(EPOCHS):
        start = time.time()

        for image_batch in train_dataset:
            train_step(image_batch)

        # Produce immagini per il GIF
        #generate_and_save_images(generator, epoch + 1, seed)

        # Stampa le metriche di loss alla fine di ogni epoca
        print('Time for epoch {} is {} sec'.format(epoch + 1, time.time() - start))

        # Puoi anche decidere di salvare i modelli solo all'ultima epoca
        if epoch == EPOCHS - 1:
            generator.save('generator_final.h5')
            discriminator.save('discriminator_final.h5')


def generate_and_save_images(model, epoch, test_input):
    # Attenzione che `training` è settato a False.
    # Ciò è così perché in modalità inferenza (batchnorm) si comporta diversamente.
    predictions = model(test_input, training=False)

    fig = plt.figure(figsize=(4, 4))

    for i in range(predictions.shape[0]):
        plt.subplot(4, 4, i + 1)
        plt.imshow(predictions[i, :, :, 0] * 127.5 + 127.5, cmap='gray')
        plt.axis('off')

    plt.savefig('image_at_epoch_{:04d}.png'.format(epoch))
    plt.show()


# Funzione per il caricamento e il preprocessing delle immagini
def load_and_preprocess_image(image_path):
    image = tf.io.read_file(image_path)
    image = tf.image.decode_jpeg(image, channels=3)  # Usa decode_png se le immagini sono in formato PNG
    image = tf.image.resize(image, [360, 250])
    image = (image / 127.5) -1  # Normalizzazione dei pixel a [-1, 1]
    return image


if __name__ == '__main__':
     #train()
     generator = load_model('generator_final.h5')  # Assicurati che il percorso sia corretto
     # Genera rumore
     noise = np.random.normal(0, 1, size=(32, noise_dim))  # Assumendo che la dimensione del rumore sia 100

     # Genera l'immagine
     generated_image = generator.predict(noise)
     tensor = np.array(generated_image, dtype=np.uint8)

     if np.ndim(tensor) > 3:
         assert tensor.shape[0] == 1
         tensor = tensor[0]

     image= Image.fromarray(tensor)

     image.save('generated_image.png')

