# extract the principal components and then passed into the script which is an Python two

from IPython import embed
import images_pca
import cv2
import scipy.stats
import scipy.io
import sklearn.metrics.pairwise as k
import pickle

IMAGES_PCA_FILE_PATH = '/n/holystore01/LABS/gershman_lab/Users/mtomov13/VGDL/images/images_pca_frame=429999.pkl'
IMAGES_PCA_FILE_PATH_PYTHON_2 = '/n/holystore01/LABS/gershman_lab/Users/mtomov13/VGDL/images/images_pca_frame=429999_python_2.pkl'

# load PCA results
with open(IMAGES_PCA_FILE_PATH, 'rb') as f:
    frames_pca = pickle.load(f)

d = {'components': frames_pca.components_,
     'mean': frames_pca.mean_}
with open(IMAGES_PCA_FILE_PATH_PYTHON_2, 'wb') as f:
    pickle.dump(d, f, protocol=2)

print('safe to', IMAGES_PCA_FILE_PATH_PYTHON_2)
