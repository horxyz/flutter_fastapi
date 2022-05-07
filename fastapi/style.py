from __future__ import absolute_import, division, print_function, unicode_literals

import matplotlib.pylab as plt
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import pandas as pd
from PIL import Image
import io

TFLITE_MODEL = "tflite_models/selfie2anime.tflite"

# Load TFLite model and see some details about input/output

tflite_interpreter = tf.lite.Interpreter(model_path=TFLITE_MODEL)

# input_details = tflite_interpreter.get_input_details()
# output_details = tflite_interpreter.get_output_details()
# Load the input images.
# content_image = load_img('F:/GraduationProject/image/demo.jpeg')

def img_bytes_to_array(img_bytes: io.BytesIO) -> tf.Tensor:
    """Loads an image from a img bytes into a tf tensor.
    Rescales RGB [0..255] to [0..1] and adds batch dimension.
    """
    img = tf.keras.preprocessing.image.img_to_array(
        Image.open(img_bytes)
    )
    img = img / 255  # convert [0..255] to float32 between [0..1]
    img = img[tf.newaxis, :]  # add batch dimension
    return img


def array_to_img_bytes(img_array: tf.Tensor) -> io.BytesIO:
    """Loads a tf tensor image into a img bytes.
    Rescales [0..1] to RGB [0..255] and removes batch dimension.
    """
    if len(img_array.shape) > 3:  # remove batch dimension
        img_array = tf.squeeze(img_array, axis=0)
    img_array = img_array * 255  # convert [0..1] back to [0..255]
    img = tf.keras.preprocessing.image.array_to_img(img_array)
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='jpeg')
    img_buffer.seek(0)
    return img_buffer

# Function to pre-process by resizing an central cropping it.
def preprocess(img_tensor: tf.Tensor, target_dim: int) -> tf.Tensor:
    """Pre-process by resizing an central cropping it."""
    # Resize the image so the shorter dimension becomes target_dim.
    shape = tf.cast(tf.shape(img_tensor)[1:-1], tf.float32)
    short_dim = min(shape)
    scale = target_dim / short_dim
    new_shape = tf.cast(shape * scale, tf.int32)
    img = tf.image.resize(img_tensor, new_shape)

    # Central crop the image so both dimensions become target_dim.
    img = tf.image.resize_with_crop_or_pad(img, target_dim, target_dim)
    return img

def style_transfer(content_image: io.BytesIO)-> io.BytesIO:
	preprocessed_content_image = preprocess(img_bytes_to_array(content_image), 256)
	interpreter = tf.lite.Interpreter(TFLITE_MODEL)

	interpreter.allocate_tensors()
	# Get input and output tensors.
	input_details = interpreter.get_input_details()
	output_details = interpreter.get_output_details()

	# Test the model on random input data.
	input_shape = input_details[0]['shape']
	input_data = preprocessed_content_image
	interpreter.set_tensor(input_details[0]['index'], input_data)

	interpreter.invoke()

	# The function `get_tensor()` returns a copy of the tensor data.
	# Use `tensor()` in order to get a pointer to the tensor.
	output_data = interpreter.get_tensor(output_details[0]['index'])
	output_img = array_to_img_bytes(output_data)
	return output_img

