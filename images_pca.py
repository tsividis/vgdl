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
from fmri_makeMovie import videosDir, imagesDir

print(videosDir, imagesDir) 

filename = 'images_pca.pkl'
filepath = os.path.join(imagesDir, filename)

def process_frame(img):
    # convert and resize
    img = img.astype(np.uint8)
    img = img / 255
    return img.flatten()

if __name__ == '__main__':

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
            all_frames.append(process_frame(img))

            print 'frame ', len(all_frames), ': ', path

    all_frames = np.concatenate([np.reshape(frame, (1,len(frame))) for frame in all_frames], axis=0)
    unique_frames = np.unique(all_frames, axis=0)
    del all_frames

    frames = pd.DataFrame(unique_frames)
    del unique_frames

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

    with open(filepath, 'wb') as f:
        cloudpickle.dump(frames_pca, f)

    fig, axes = plt.subplots(2,2,figsize=(2,2),
        subplot_kw={'xticks':[], 'yticks':[]},
        gridspec_kw=dict(hspace=0.01, wspace=0.01))
    for i, ax in enumerate(axes.flat):
        ax.imshow(frames_pca.components_[i].reshape(*img.shape))
    plt.show()


