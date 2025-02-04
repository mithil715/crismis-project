# -*- coding: utf-8 -*-
"""mithil_gsoc.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gJSatrnpDzwOMwUVAG3sXm2aFpgiNA6M

1.   Looking at model from starting we see that our model takes an input of year, date , and image_name, saves it and plots the image
2.  Afterwards model provides two images that we were told to plot
1.   Model downloads all the images and creates a dataset
2.  Model segregates dataset into two, one cointaining images that have cosmic rays and other cointaining images that do not have cosmic rays
5.Then it stores the images and there corresponding labels into pickle format
6.Afterward training with 300 epochs takes place and then the model is tested by finding whether it predicts 1 or 0 for an image given, whose label we know
"""

!pip install ccdproc planetaryimage

!pip install wget

# Commented out IPython magic to ensure Python compatibility.
from urllib.request import Request, urlopen, urlretrieve
from bs4 import BeautifulSoup
import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt
from PIL import Image  
# %matplotlib inline
from planetaryimage import PDS3Image
# plt.switch_backend('agg')jp
import scipy.misc
import subprocess
import numpy as np
from astropy import units as u
from astropy.nddata import CCDData
import ccdproc
import imageio
import subprocess
import os
from tqdm import tqdm
import random
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
import pickle
import cv2
import tensorflow as tf
import planetaryimage
from torchvision.utils import save_image
import scipy.misc
import subprocess
import matplotlib.image as mpimg
import imageio
import os
import wget
import glob



"""[[[STEP 1]]]


*   **In this portion our models ask to enter year, day, image_name and saves and shows the given image**
*   In the following code the IMG_dataset is dataset which stores images in .IMG form, and png_dataset is the dataset which stores images in .png form of the given year and date of year.
"""

year=input("Enter year: ")
day=input("Enter day: ")
url="https://pdsimage2.wr.usgs.gov/archive/mess-e_v_h-mdis-2-edr-rawdata-v1.0/MSGRMDS_1001/DATA/%s_%s/" % (year, day)
url = url.replace(" ","%20")
req = Request(url)
a = urlopen(req).read()
soup = BeautifulSoup(a, 'html.parser')
x = (soup.find_all('a'))
os.makedirs('IMG_dataset', exist_ok=True)
os.makedirs('png_dataset', exist_ok=True)
extensions = ['.IMG']
        

for i in x:
    file_name = i.extract().get_text()
    url_new = url + file_name
    url_new = url_new.replace(" ","%20")
    if url_new.endswith('.IMG'):
        img_name=url_new[-17:]
        subprocess.call(['wget', url_new])
        subprocess.call('mv %s "./IMG_dataset/"' % (str(img_name)), shell=True)
        
input_dir='./IMG_dataset'
for IMG in (os.listdir(input_dir)): 
    try:
       if IMG.endswith("IMG"):  
        img = os.path.join(input_dir, IMG)   
        image = PDS3Image.open(img)
        imageio.imwrite('./png_dataset/%s.png' % (IMG[:-4]), image.image)
    except Exception as e:
        pass

images = []
for img_path in glob.glob('./png_dataset/*.png'):
    images.append(mpimg.imread(img_path))

plt.figure(figsize=(20,10))
columns = 5
for i, image in enumerate(images):
    plt.subplot(len(images) / columns + 1, columns, i + 1)
    plt.imshow(image,cmap='gray')

"""**This portion saves and shows the first image**"""

url1="https://pdsimage2.wr.usgs.gov/archive/mess-e_v_h-mdis-2-edr-rawdata-v1.0/MSGRMDS_1001/DATA/2011_207/EW0220137668G.IMG"
img_name1="EW0220137668G.IMG" 

subprocess.call(['wget', url1])
image = PDS3Image.open(img_name1)

plt.imshow(image.image, cmap='gray')
plt.show()
           
subprocess.call('rm -r %s' % (str(img_name1)), shell=True)

"""**This portion saves and shows the second image**"""



url2="https://pdsimage2.wr.usgs.gov/archive/mess-e_v_h-mdis-2-edr-rawdata-v1.0/MSGRMDS_1001/DATA/2014_215/EN1049375684M.IMG"
img_name2="EN1049375684M.IMG"

subprocess.call(['wget', url2])
image = PDS3Image.open(img_name2)
plt.imshow(image.image, cmap='gray')
plt.show()
           
subprocess.call('rm -r %s' % (str(img_name2)), shell=True)

"""[[[STEP 2]]]
**This portion is for downloading the dataset into png format**
"""

os.makedirs('./dataset', exist_ok=True)
os.makedirs('./data', exist_ok=True)
os.makedirs('./data/0', exist_ok=True)
os.makedirs('./data/1', exist_ok=True)

def read_url(url):
    url = url.replace(" ","%20")
    req = Request(url)
    a = urlopen(req).read()
    soup = BeautifulSoup(a, 'html.parser')
    x = (soup.find_all('a'))
    for i in x:
        file_name = i.extract().get_text()
        url_new = url + file_name
        url_new = url_new.replace(" ","%20")
        if(file_name[-1]=='/' and file_name[0]!='.'):
            try:
                read_url(url_new)
            except Exception as e:
                 pass
        elif(file_name[-1]=='G'):
                if(url_new[-1]=='G'):
                   img_name=url_new[-17:]
                   subprocess.call(['wget', url_new])
                   image = PDS3Image.open(img_name)
                   imageio.imwrite('./dataset/%s.png' % (img_name[:-4]), image.image)
                   #subprocess.call(['rm -r', img_name])
                   subprocess.call('rm -r %s' % (str(img_name)), shell=True)
            
read_url("https://pdsimage2.wr.usgs.gov/archive/mess-e_v_h-mdis-2-edr-rawdata-v1.0/MSGRMDS_1001/DATA/")
#tried my code on fraction of dataset to check it's working

"""**This portion is for detecting cosmic and non_cosmic rays and creating two seperate folders one cointaning cosmic rays(name='1') and another without cosmic ray(name='0')**"""

input_dir = './dataset'

for IMG in (os.listdir(input_dir)):
  try:
   if IMG.endswith("png"):     
     img = os.path.join(input_dir, IMG)
    
     data = imageio.imread(img)
     _, mask = ccdproc.cosmicray_lacosmic(data, sigclip=5)
     if np.sum(mask)>=1:
      	subprocess.call('cp %s ./data/%s/' % (str(img), str(0)), shell=True)#it will store all the images containing cosmic rays in a directory named data, and in that a subdirectory named 1
     else:
      	subprocess.call('cp %s ./data/%s/' % (str(img), str(1)), shell=True)#it will store all the images not containing cosmic rays in a directory named data, and in that a subdirectory named 0
  except Exception as e:
         pass

"""**This portion saves the images(name='train_x.pickle') and there labels(name='train_y.pickle') in pickle format and creates label for the images**"""

DATADIR = "./data"
os.makedirs(DATADIR, exist_ok=True)
CATEGORIES = ["0", "1"]
IMG_SIZE = 50

# prepare training data
training_data = []
def create_training_and_testing_data():
    for category in CATEGORIES:  # do cosmic and non-cosmmic
        path = os.path.join(DATADIR,category)  # create path to cosmic and non-cosmic
        class_num = CATEGORIES.index(category)  # get the classification  (0 or a 1). 0=no_cosmic 1=cosmic
        for img in tqdm(os.listdir(path)):  # iterate over each image per cosmic and non-cosmic
            try:
                #img_array = cv2.imread(os.path.join(path,img), cv2.IMREAD_GRAYSCALE)  # convert to array
                img_array = cv2.imread(os.path.join(path,img), cv2.IMREAD_GRAYSCALE)  # convert to array
                new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))  # resize to normalize data size
                training_data.append([new_array, class_num])  # add this to our training_data
            except Exception as e:  # in the interest in keeping the output clean...
                pass

create_training_and_testing_data()
#shuffle data
random.shuffle(training_data)

x = []
y = []
for features,label in training_data:
    x.append(features)
    y.append(label)
    

x = np.array(x).reshape(-1, IMG_SIZE, IMG_SIZE, 1)

#1. save training data
pickle_out = open("train_x.pickle","wb")
pickle.dump(x, pickle_out)
pickle_out.close()

pickle_out = open("train_y.pickle","wb")
pickle.dump(y, pickle_out)
pickle_out.close()

"""[[[STEP 3]]]
**This portion is for training the model over the downloaded dataset**
"""

pickle_in = open("train_x.pickle","rb")
x_train = pickle.load(pickle_in)
pickle_in = open("train_y.pickle","rb")
y_train = pickle.load(pickle_in)

x_train = x_train/255.0  #range: 0-to-1

model = Sequential()
model.add(Conv2D(256, (3, 3), input_shape=x_train.shape[1:]))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(256, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())  # this converts our 3D feature maps to 1D feature vectors
model.add(Dense(64))
model.add(Dense(1))
model.add(Activation('sigmoid'))

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(x_train, y_train, batch_size=32, epochs=4, validation_split=0.3)     #for validation we take 30% of the available dataset, and 70% for training

model.save('cosmic.model')# this saves our model

"""**This portion is for testing our model,Here our model will predict whether the given image consists of cosmic ray artifacts or not**"""

CATEGORIES = ["0", "1"]  # will use this to convert prediction num to string value
import numpy
def prepare(filepath):
    IMG_SIZE = 50          #here we convert our input image to size which is compatible with size of the images on which we had performed the training of the
    im = Image.open(filepath)  
   # img_array = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)  # read in the image, convert to grayscale
    newsize = (50, 50) 
    im = im.resize(newsize) 
    greyscale_map = list(im.getdata())
    greyscale_map = numpy.array(greyscale_map)
    #new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))  # resize image to match model's expected sizing
    return greyscale_map.reshape(-1, IMG_SIZE, IMG_SIZE, 1)  # return the image with shaping that TF wants.

#load model
model = tf.keras.models.load_model("cosmic.model")

#make predicition
prediction = model.predict([prepare('./png_dataset/EW0220137668G.png')])   #for this image the answer should be it contains cosmic ray artifacts
if(int(CATEGORIES[int(prediction[0][0])])==1):    #If the answer is 1 then it contains cosmic ray artifacts, if the answer is 0 then it does not contain cosmic ray artifacts
  print('It contains cosmic ray artifacts' )
elif(int(CATEGORIES[int(prediction[0][0])])==0):
  print('It does not contains cosmic ray artifacts')

"""**end of the model**"""

