# ! pip install git+https://github.com/rcmalli/keras-vggface.git
# !pip install keras_applications --no-deps
import cv2
from keras_vggface import utils
from keras_vggface.vggface import VGGFace
from keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
import keras_vggface
import tensorflow as tf
# filename = "/usr/local/lib/python3.7/dist-packages/keras_vggface/models.py"
# text = open(filename).read()
# open(filename, "w+").write(text.replace('keras.engine.topology', 'tensorflow.keras.utils'))

# from google.colab.patches import cv2_imshow

model = VGGFace(model='resnet50', include_top=False,
                input_shape=(224, 224, 3), pooling='avg')


def carre(path):
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    img = cv2.imread(path)
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    print(faces)
    x, y, w, h = faces[0]
    dmc = img[y:y+h, x:x+w]
    # path_carre = 'carre_' + path
    path_carre = path
    cv2.imwrite(path_carre, dmc)
    return path_carre


vecteurs_predict = []
liste_noms = ['alpha.jpg', 'beta.jpg', 'gamma.jpg', 'delta.jpg']
liste_noms_carre = []
for x in liste_noms:
    x = './data_base/' + x
    print(x)
    path_carre = carre(x)
    liste_noms_carre.append(path_carre)
    img = tf.keras.utils.load_img(path_carre, target_size=(224, 224))
    y = tf.keras.utils.img_to_array(img)
    y = np.expand_dims(y, axis=0)
    y = utils.preprocess_input(y, version=1)
    preds = model.predict
    vecteurs_predict.append((path_carre, preds))


def test(adresse_image):
    adresse_carre = carre(adresse_image)
    img_new = tf.keras.utils.load_img(adresse_carre, target_size=(224, 224))
    x = tf.keras.utils.img_to_array(img_new)
    x = np.expand_dims(x, axis=0)
    x = utils.preprocess_input(x, version=1)
    preds_new = model.predict(x)
    m = []
    for element in vecteurs_predict:
        vecteur_ecart = list(preds_new - element[1])
        f = list(vecteur_ecart[0])
        l = [abs(i) for i in f]
        s = sum(l)/len(l)
        m.append((element, s))
    l = [i[1] for i in m]
    for j in m:
        if j[1] == min(l):
            return (j[0][0])
