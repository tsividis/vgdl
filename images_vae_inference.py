from images_vae import read_image_for_vae, VariationalEncoder, Decoder, VariationalAutoencoder
import matplotlib.pyplot as plt # plotting library
import numpy as np # this module is useful to work with numerical arrays
import pandas as pd 
import random 
import torch
import torchvision
from torchvision import transforms
from torch.utils.data import DataLoader,random_split
from torch import nn
import torch.nn.functional as F
import cloudpickle
import torch.optim as optim
from IPython import embed

import os
import torch
import pandas as pd
from skimage import io, transform
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
import images_pca
import random
import numpy as np
import cv2
import matplotlib.pyplot as plt
import time
from glob import iglob
import pandas as pd
from skimage.transform import resize
from IPython import embed
from sklearn.decomposition import PCA, IncrementalPCA
import torchvision.transforms as T
from PIL import Image
import socket
import os
import cloudpickle

if __name__ == '__main__':
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

    rootDir = os.path.join(images_pca.imagesDir, 'DQN')
    all_frame_files = images_pca.get_all_frame_files(rootDir)

    vae = torch.load('/n/holystore01/LABS/gershman_lab/Users/mtomov13/VGDL/images/VAE/training/images_vae_epoch=9999_final.pt')
    vae.to(device)

    for i in range(len(all_frame_files)):

        path = all_frame_files[i]
        img = read_image_for_vae(path)

        with torch.no_grad():
            embedding = vae.encoder(img.unsqueeze(0).to(device))

        new_path = path.replace('DQN', 'VAE').replace('png', 'pkl')
        new_path = new_path.replace('/n/holystore01/LABS/gershman_lab/Users/mtomov13/', '/n/holyscratch01/LABS/gershman_lab/Users/mtomov13/')

        os.makedirs(os.path.split(new_path)[0], exist_ok=True)

        with open(new_path, 'wb') as f:
            cloudpickle.dump({'embedding': embedding.detach().cpu().squeeze().numpy()}, f, protocol=2)
