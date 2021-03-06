# -*- coding: utf-8 -*-
"""Submission: Image Classification2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kA8JX9tdUp642Cxuu1TRNCUxYGPMd8FU

import library
"""

import pandas as pd
import tensorflow as tf
import os

from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, Sequential
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv2D, Activation, MaxPooling2D, Dropout, Flatten, Dense
from keras.applications.inception_v3 import InceptionV3

"""data preparation (data sudah dibagi 80:20 manual)"""

#dir training
train_dir = '/content/drive/My Drive/catsanddogs/training_set'
train_cats_dir = os.path.join(train_dir, 'cats')
train_dogs_dir = os.path.join(train_dir, 'dogs')

#dir test
test_dir = '/content/drive/My Drive/catsanddogs/test_set'
test_cats_dir = os.path.join(test_dir, 'cats')
test_dogs_dir = os.path.join(test_dir, 'dogs')

"""image augmentation"""

train_datagen = ImageDataGenerator(
                     rescale=1./255,
                     rotation_range=20,
                     horizontal_flip=True,
                     shear_range = 0.2,
                     fill_mode = 'nearest')
     
test_datagen = ImageDataGenerator(
                    rescale=1./255,
                    rotation_range=20,
                    horizontal_flip=True,
                    shear_range = 0.2,
                    fill_mode = 'nearest')

"""prepare training data for model training"""

train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(150, 150),
        batch_size=128,
        class_mode='binary')
     
test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=(150, 150),
        batch_size=128, 
        class_mode='binary')

"""model"""

inceptionV3 = InceptionV3(include_top= False, input_shape=(150,150,3))
for layer in inceptionV3.layers:
	layer.trainable = False

model = tf.keras.models.Sequential([
    inceptionV3, 
    tf.keras.layers.Conv2D(64, (3,3), padding='same', activation='relu'),
    tf.keras.layers.MaxPooling2D(3,3),
    tf.keras.layers.Dropout(0.4),  
    tf.keras.layers.Flatten(), 
    tf.keras.layers.Dense(1024, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(1, activation='sigmoid')  
])

"""optimizer and loss function"""

model.compile(loss='binary_crossentropy',
              optimizer=tf.optimizers.Adam(),
              metrics=['accuracy'])

"""callbacks"""

class callback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy') > 0.92):
      self.model.stop_training = True

callbacks = callback()

"""training model"""

history = model.fit(train_generator,
                    epochs = 100,
                    verbose = 1,
                    validation_data = test_generator,
                    callbacks=[callbacks])

"""plot accuracy"""

import matplotlib.pyplot as plt

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Plot Accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""plot loss"""

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Plot Loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""convert to tflite"""

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

#menyimpan model ke model.tflite
with tf.io.gfile.GFile('model.tflite', 'wb') as f:
  f.write(tflite_model)