# do PCA on image sequence to extract features (generated using fmri_makeMovie.py)
# based on DQN fMRI paper
# https://medium.com/@sebastiannorena/pca-principal-components-analysis-applied-to-images-of-faces-d2fc2c083371
# note that it requires python 3

import random
import numpy as np
import cv2
import matplotlib.pyplot as plt
import time
from glob import iglob
import pandas as pd
from IPython import embed
from sklearn.decomposition import PCA, IncrementalPCA
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
print('images_pca dirs: ', videosDir, imagesDir)

batch_size = 10000 # how many frames to accumulate before running PCA
n_components = 30 # TODO param

def process_frame(img):
    # convert and resize
    img = img.astype(np.uint8)
    img = img / 255
    return img.flatten()

random.seed(0)

if __name__ == '__main__':
    game_name = int(sys.argv[1])

    filename = 'images_pca_{}.pkl'.format(game_name)
    filepath = os.path.join(imagesDir, filename)
    print('images_pca output filepath: ', filepath)

    #rootDir = os.path.join(imagesDir, 'makeMovie')
    rootDir = os.path.join(imagesDir, 'DQN')

    # first collect all images
    all_frame_files = []
    for dirName, subdirList, fileList in os.walk(rootDir):
        print('Found directory: %s' % dirName)
        for fname in fileList:
            if not fname.endswith('.png'):
                continue
            if not fname.startswith('fmri_agentReplay_DQN'):
                continue
            if not fname.contains(game_name):
                continue
            path = os.path.join(dirName, fname)
            print('\t%s' % path)
            all_frame_files.append(path)

    # go in random order because of autocorrelation 
    random.shuffle(all_frame_files)

    # run incremental PCA and keep saving results
    #
    frames_pca = IncrementalPCA(n_components=n_components, batch_size=batch_size)
    all_frames = []
    for i, path in enumerate(all_frame_files): 
        img = cv2.imread(path)
        all_frames.append(process_frame(img))

        # optionally run PCA
        print(i, 'frame ', len(all_frames), ': ', path)
        if len(all_frames) >= batch_size:
            then = time.time()

            all_frames = np.concatenate([np.reshape(frame, (1,len(frame))) for frame in all_frames], axis=0)
            # remove duplicates & clear original array
            unique_frames = np.unique(all_frames, axis=0)
            all_frames = []
            # convert to pd
            frames = pd.DataFrame(unique_frames)
            del unique_frames

            # run incremental PCA
            print('   running incremental PCA with ', len(frames), 'unique frames')
            frames_pca.partial_fit(frames)

            print('         PCA took ', time.time() - then, 's')

            # save results so far
            with open(filepath, 'wb') as f:
                cloudpickle.dump(frames_pca, f)


    # visualize
    #
    #fig, axes = plt.subplots(9,9,figsize=(9,9),
    #subplot_kw={'xticks':[], 'yticks':[]},
    #gridspec_kw=dict(hspace=0.01, wspace=0.01))
    #for i, ax in enumerate(axes.flat):
    #    ax.imshow(frames.iloc[i].values.reshape(*img.shape))
    #plt.show()
    

    ## run PCA
    ##
    #frames_pca = PCA(n_components=0.9)
    ##frames_pca = PCA(n_components=30)
    #frames_pca.fit(frames)

    #embed()

    fig, axes = plt.subplots(2,2,figsize=(2,2),
        subplot_kw={'xticks':[], 'yticks':[]},
        gridspec_kw=dict(hspace=0.01, wspace=0.01))
    for i, ax in enumerate(axes.flat):
        ax.imshow(frames_pca.components_[i].reshape(*img.shape))
    plt.show()
