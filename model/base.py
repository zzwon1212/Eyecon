# -*- coding: utf-8 -*-
"""Base.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xYElMfIX7hRSMvtQq8ADrhG8Qxi9bmMp

# Base
"""

import json
import pandas as pd
import re
import numpy as np
from sklearn.model_selection import train_test_split
import cv2
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import Model, Sequential, load_model
from tensorflow.keras.layers import Input, Dense, Conv2D, MaxPooling2D, ZeroPadding2D, Dropout, Flatten, Activation, Concatenate

import inspect
import os


# ====================================
with open(r'C:\Users\sodaus\Desktop\data\ver4-6\metadata_ver4-6_merge.json') as json_file:
    meta = json.load(json_file)
    
meta_df = pd.DataFrame()
meta_df['frame_name'] = list(x['facelmname'][:-11] for x in meta['data'])
# 0_ver3_LDH1_frame0
meta_df['video_name'] = list(x['file_name'] for x in meta['data'])
# 0_free_ver3_LDH1.mp4
meta_df['subject'] = list(''.join(re.compile('[A-Z]').findall(x['subject'])) for x in meta['data'])
# LDH
# meta_df['head_pose'] = list([(np.array(list(x['head_pose'].values())).astype('float')) for x in meta['data']])
# [-6.73000491 22.94420144 -3.0902351 ]
meta_df['head_pose'] = list([(np.array(list(x['head_pose'].values())).astype('float')) for x in meta['data']])
meta_df['face_landmarks'] = list([(x['face_landmarks']) for x in meta['data']])
meta_df['faceimg_name'] = list(x['facelmname'] for x in meta['data'])
# 0_ver3_LDH1_frame0_facelm.jpg
meta_df['lefteyeimg_name'] = list(x['eyelmname'][0] for x in meta['data'])
# 0_ver3_LDH1_frame0_eyelm_left.jpg
meta_df['righteyeimg_name'] = list(x['eyelmname'][1] for x in meta['data'])
# 0_ver3_LDH1_frame0_eyelm_right.jpg
meta_df['label'] = list(x['label'] for x in meta['data'])



# ====================================
# meta_df = pd.read_csv('/content/drive/Shared drives/H1L4/meta_df.csv')
# meta_df.drop('Unnamed: 0', axis=1,inplace=True)

train, valid = train_test_split(meta_df, test_size=0.2, random_state=42)
train.reset_index(drop=True, inplace=True)
valid.reset_index(drop=True, inplace=True)

path = 'C:/Users/sodaus/Desktop/data/ver4-6/img/'

def gen(dataframe, label=False):
  if bool(label) == False:
    for i in range(len(dataframe)):
      face_img = tf.cast(cv2.cvtColor(cv2.imread(path + dataframe['faceimg_name'][i]), cv2.COLOR_BGR2RGB), tf.float32)
      eyeleft_img = tf.cast(cv2.cvtColor(cv2.imread(path + dataframe['lefteyeimg_name'][i]), cv2.COLOR_BGR2RGB), tf.float32)
      eyeright_img = tf.cast(cv2.cvtColor(cv2.imread(path + dataframe['righteyeimg_name'][i]), cv2.COLOR_BGR2RGB), tf.float32)
      headpose = dataframe['head_pose'][i]
      yield(face_img, eyeleft_img, eyeright_img, headpose)
  else:
    for i in range(len(dataframe)):
      label = dataframe['label'][i]
      yield(label)
# def y_gen(dataframe):
#   for i in range(len(dataframe)):
#     label = dataframe['label'][i]
#     yield(label)

x_train_ds = tf.data.Dataset.from_generator(
    lambda: gen(train),
    (tf.float32, tf.float32, tf.float32, tf.float32),
    (tf.TensorShape([300, 300, 3]), tf.TensorShape([100, 100, 3]), tf.TensorShape([100, 100, 3]), tf.TensorShape([3]))
)
y_train_ds = tf.data.Dataset.from_generator(
    lambda: gen(train, label=True),
    (tf.int32),
    (tf.TensorShape([]))
)
x_valid_ds = tf.data.Dataset.from_generator(
    lambda: gen(valid),
    (tf.float32, tf.float32, tf.float32, tf.float32),
    (tf.TensorShape([300, 300, 3]), tf.TensorShape([100, 100, 3]), tf.TensorShape([100, 100, 3]), tf.TensorShape([3]))
)
y_valid_ds = tf.data.Dataset.from_generator(
    lambda: gen(valid, label=True),
    (tf.int32),
    (tf.TensorShape([]))
)



# ================================
IMAGE_SIZE = 224
BATCH_SIZE = 32

add_noise = tf.keras.Sequential([tf.keras.layers.GaussianNoise(0.08)])
def augment(face, eyeleft, eyeright, headpose):
  face = tf.image.resize(face, [IMAGE_SIZE, IMAGE_SIZE]) / 255.0
  eyeleft = tf.image.resize(eyeleft, [IMAGE_SIZE, IMAGE_SIZE]) / 255.0
  eyeright = tf.image.resize(eyeright, [IMAGE_SIZE, IMAGE_SIZE]) / 255.0
  image_set = tf.image.random_brightness([face, eyeleft, eyeright], max_delta=0.15)
  image_set = tf.image.random_contrast(image_set, 0.7, 1.3)
  image_set = tf.image.random_hue(image_set, 0.05)  #  색조, 0 < x < 0.5 .05
  image_set = tf.image.random_saturation(image_set, 0.7, 2.0)  # 채도
  image_set = add_noise(image_set, training=True)
  image_set = tf.clip_by_value(image_set, 0, 1)  # https://stackoverrun.com/ko/q/12304559
  face, eyeleft, eyeright = image_set[0], image_set[1], image_set[2]
  return face, eyeleft, eyeright, headpose

def resize_and_rescale(face, eyeleft, eyeright, headpose):
  # image = tf.cast(image, tf.float32)  # ????? 아마 필요없을 듯 이미 float32라서
  face = tf.image.resize(face, [IMAGE_SIZE, IMAGE_SIZE]) / 255.0
  eyeleft = tf.image.resize(eyeleft, [IMAGE_SIZE, IMAGE_SIZE]) / 255.0
  eyeright = tf.image.resize(eyeright, [IMAGE_SIZE, IMAGE_SIZE]) / 255.0
  return face, eyeleft, eyeright, headpose

AUTOTUNE = tf.data.experimental.AUTOTUNE
train_ds = (tf.data.Dataset.zip((x_train_ds.cache().map(augment, num_parallel_calls=AUTOTUNE), 
                                 y_train_ds))
    .batch(BATCH_SIZE)
    .prefetch(AUTOTUNE)
)
valid_ds = (tf.data.Dataset.zip((x_valid_ds.cache().map(resize_and_rescale, num_parallel_calls=AUTOTUNE), 
                                 y_valid_ds))
    .batch(BATCH_SIZE)
    .prefetch(AUTOTUNE)
)



# ====================================
# zip plot
# num_batch: 3
# input type: 3
# frame in batch: 4
# list_train_ds = list(train_ds)
# plt.figure(figsize=(3, 16))
# for num_batch in range(3):
#   for frame_in_batch in range(4):
#     for input_type in range(3):
#       # print(12*(num_batch) + 3*(frame_in_batch) + input_type + 1)
#       plt.subplot(12, 3, (12*(num_batch) + 3*(frame_in_batch) + input_type + 1))
#       plt.imshow(list_train_ds[num_batch][0][input_type][frame_in_batch])
#       plt.axis('off')



# ==============================
# Face
from tensorflow.keras.applications import MobileNetV2
base_model_face = MobileNetV2(input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3),
                              include_top=False,
                              weights='imagenet',
                              pooling='avg')
for layer in base_model_face.layers:
    layer.trainable = False
face = Dense(128, activation='relu', name='face_fc_1')(base_model_face.output)  # same with [Krafka]
face = Dense(64, activation='relu', name='face_fc_2')(face)  # same with [Krafka]

# Eye shared weights and fc before concat
input_eyeleft = Input(shape=(224, 224, 3))
input_eyeright = Input(shape=(224, 224, 3))
class eye_layers(tf.keras.layers.Layer):
  
  def __init__(self):
    super(eye_layers, self).__init__()
    self.ZeroPad_1 = ZeroPadding2D(padding=(1, 1))
    self.Conv_1 = Conv2D(64, (3, 3), activation='relu')
    self.MaxPool_1 = MaxPooling2D(pool_size=(2, 2))
    self.ZeroPad_2 = ZeroPadding2D(padding=(1, 1))
    self.Conv_2 = Conv2D(128, (3, 3), activation='relu')
    self.MaxPool_2 = MaxPooling2D(pool_size=(2, 2))

  def call(self, inputs):
    eye = self.ZeroPad_1(inputs)
    eye = self.Conv_1(eye)
    eye = self.MaxPool_1(eye)
    eye = self.ZeroPad_2(eye)
    eye = self.Conv_2(eye)
    return self.MaxPool_2(eye)
eye_layers_ = eye_layers()
eyeleft = eye_layers_(input_eyeleft)
eyeright = eye_layers_(input_eyeright)
eyes = tf.keras.layers.concatenate([eyeleft, eyeright])
eyes = tf.keras.layers.GlobalAveragePooling2D()(eyes)
# eyes = Flatten()(eyes)
eyes = Dense(64, activation='relu', name='eyes_fc1')(eyes)  # 128 [Krafka]

# headpose
input_headpose = Input(shape=(3), name='headpose')  # same with [Zhang], [Palmero]

# Concat
main = tf.keras.layers.concatenate([face, eyes, input_headpose])
main = Dense(128, activation='relu', name='main_fc1')(main)  # same with [Krafka]
# x_5 = Dense(????, activation='relu')(x_5)  # same with [Palmero]
# x_5 = Dense(????, activation='relu')(x_5)  # same with [Palmero]
output_main = Dense(1, activation='sigmoid', name='main_fc2')(main)  # same with [Krafka]

LEARNING_RATE = 0.001
model = Model(inputs=[base_model_face.input, input_eyeleft, input_eyeright, input_headpose],
              outputs=output_main)
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE), 
              loss=tf.losses.BinaryCrossentropy(),
              metrics=['accuracy'])
model.summary()



# =============================
checkpoint_path = "C:/Users/sodaus/Desktop/1stmodel/model_name"
cb_checkpoint = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                   monitor='val_loss',
                                                   save_weights_only=False,
                                                   save_best_only=True,
                                                   verbose=2)
cb_earlystopper = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                   patience=5)
with tf.device('/device:GPU:0'):
  fit_history = model.fit(
      train_ds,
      epochs=5,
      validation_data=valid_ds,
      callbacks=[cb_checkpoint, cb_earlystopper]
  )



# ==============================
import matplotlib.pyplot as plt
plt.subplot(2, 1, 1)
plt.plot(fit_history.history["accuracy"])
plt.plot(fit_history.history['val_accuracy'])
plt.title("Accuracy")
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.legend(["Accuracy", "Val Accuracy"])
plt.subplot(2, 1, 2)
plt.plot(fit_history.history["loss"])
plt.plot(fit_history.history["val_loss"])
plt.title("Loss")
plt.xlabel("Epochs")
plt.ylabel("Binary CrossEntropy")
plt.legend(["Loss", "Val Loss"])
plt.show()



# ==============================
new_model = tf.keras.models.load_model('C:/Users/sodaus/Desktop/1stmodel/model_name')
# new_model.summary()
# new_model.evaluate(valid_ds)
