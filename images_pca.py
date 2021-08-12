# do PCA on image sequence to extract features (generated using fmri_makeMovie.py)
# based on DQN fMRI paper
# https://medium.com/@sebastiannorena/pca-principal-components-analysis-applied-to-images-of-faces-d2fc2c083371
# note that it requires python 3

import numpy as np
import cv2
import matplotlib.pyplot as plt
import time
from glob import iglob
import pandas as pd
from IPython import embed
from sklearn.decomposition import PCA
import socket
import os
import cloudpickle

if 'omchil' in socket.gethostname() or 'ncfood' in socket.gethostname() or 'ncflogin' in socket.gethostname():
    # local on my Mac, or on a login / VDI node
    videosDir = 'videos'
    imagesDir = 'images'
else:
    # cluster
    videosDir = os.path.join(os.environ.get('MY_LAB'), 'VGDL', 'videos')
    imagesDir = os.path.join(os.environ.get('MY_LAB'), 'VGDL', 'images')
    print(videosDir, imagesDir) 

rootDir = os.path.join(imagesDir, 'makeMovie')

all_frames = []

for dirName, subdirList, fileList in os.walk(rootDir):
    print('Found directory: %s' % dirName)
    for fname in fileList:
        if not fname.endswith('.png'):
            continue
        path = os.path.join(dirName, fname)
        print('\t%s' % path)

        img = cv2.imread(path)
        # convert and resize
        img = img.astype(np.uint8)
        img = img / 255
        all_frames.append(img.flatten())

all_frames = np.concatenate([np.reshape(frame, (1,len(frame))) for frame in all_frames], axis=0)
unique_frames = np.unique(all_frames, axis=0)
del all_frames
#
# for path in iglob(os.path.join(imagesDir, 'makeMovie')):
#
#     print(path)

#img = cv2.imread('all_frames/pres_real_s=1_r=1_b=0_i=0_p=0_vgfmri3_chase_frame=83.png')
#img = img.astype(np.uint8)
#img = img / 255
#
#scale = 0.05
#dim = (int(img.shape[1] * scale), int(img.shape[0] * scale))
#img2 = cv2.resize(img, dim)

#plt.figure(1)
#plt.imshow(img)
#plt.figure(2)
#plt.imshow(img2)
#plt.show()
#
#embed()

#scale = 0.1
#
## extract frames into pandas series
##
#frames = pd.DataFrame([])
#i = 0
#for path in iglob('all_frames/*.png'):
#    # read image
#    img = cv2.imread(path)
#    # convert and resize
#    img = img.astype(np.uint8)
#    img = img / 255
#    dim = (int(img.shape[1] * scale), int(img.shape[0] * scale))
#    img2 = cv2.resize(img, dim)
#    # add to series
#    frame = pd.Series(img2.flatten(), name=path)
#    frames = frames.append(frame)
#    print(path)
#
#    i += 1
#    #if i == 100:
#    #    break
#
#print('shape', img2.shape, ' length ', len(frames))

frames = pd.DataFrame(unique_frames)

# visualize
#
fig, axes = plt.subplots(9,9,figsize=(9,9),
   subplot_kw={'xticks':[], 'yticks':[]},
   gridspec_kw=dict(hspace=0.01, wspace=0.01))
for i, ax in enumerate(axes.flat):
   ax.imshow(frames.iloc[i].values.reshape(*img.shape))
plt.show()
 

# run PCA
#
frames_pca = PCA(n_components=0.9)
#frames_pca = PCA(n_components=30)
frames_pca.fit(frames)

embed()

with open('images_pca.pkl', 'wb') as f:
    cloudpickle.dump(frames_pca, f)

fig, axes = plt.subplots(2,2,figsize=(2,2),
    subplot_kw={'xticks':[], 'yticks':[]},
    gridspec_kw=dict(hspace=0.01, wspace=0.01))
for i, ax in enumerate(axes.flat):
    ax.imshow(frames_pca.components_[i].reshape(*img.shape))
plt.show()


