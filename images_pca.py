# do PCA on image sequence to extract features
# based on DQN fMRI paper
# https://medium.com/@sebastiannorena/pca-principal-components-analysis-applied-to-images-of-faces-d2fc2c083371

import numpy as np
import cv2
import matplotlib.pyplot as plt
import time
from glob import iglob
import pandas as pd
from IPython import embed
from sklearn.decomposition import PCA

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

scale = 0.1

# extract frames into pandas series
#
frames = pd.DataFrame([])
i = 0
for path in iglob('all_frames/*.png'):
    # read image
    img = cv2.imread(path)
    # convert and resize
    img = img.astype(np.uint8)
    img = img / 255
    dim = (int(img.shape[1] * scale), int(img.shape[0] * scale))
    img2 = cv2.resize(img, dim)
    # add to series
    frame = pd.Series(img2.flatten(), name=path)
    frames = frames.append(frame)
    print(path)

    i += 1
    #if i == 100:
    #    break

print('shape', img2.shape, ' length ', len(frames))

# visualize
#
fig, axes = plt.subplots(9,9,figsize=(9,9),
   subplot_kw={'xticks':[], 'yticks':[]},
   gridspec_kw=dict(hspace=0.01, wspace=0.01))
for i, ax in enumerate(axes.flat):
   ax.imshow(frames.iloc[i].values.reshape(*img2.shape))
plt.show()
 
#embed()

# run PCA
#
frames_pca = PCA(n_components=0.9)
#frames_pca = PCA(n_components=30)
frames_pca.fit(frames)
fig, axes = plt.subplots(2,10,figsize=(9,3),
    subplot_kw={'xticks':[], 'yticks':[]},
    gridspec_kw=dict(hspace=0.01, wspace=0.01))
for i, ax in enumerate(axes.flat):
    ax.imshow(frames_pca.components_[i].reshape(*img2.shape))
plt.show()

embed()
