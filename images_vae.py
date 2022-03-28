# from https://medium.com/dataseries/variational-autoencoder-with-pytorch-2d359cbf027b

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

class VariationalEncoder(nn.Module):
    def __init__(self, latent_dims, num_channels, last_conv_size):  
        super(VariationalEncoder, self).__init__()
        self.conv1 = nn.Conv2d(num_channels, 8, 3, stride=2, padding=1)
        self.conv2 = nn.Conv2d(8, 16, 3, stride=2, padding=1)
        self.batch2 = nn.BatchNorm2d(16)
        self.conv3 = nn.Conv2d(16, 32, 3, stride=2, padding=0)  
        #self.linear1 = nn.Linear(3*3*32, 128) # MNIST
        self.linear1 = nn.Linear(last_conv_size * last_conv_size * 32, 128)
        self.linear2 = nn.Linear(128, latent_dims)
        self.linear3 = nn.Linear(128, latent_dims)

        self.N = torch.distributions.Normal(0, 1)
        self.N.loc = self.N.loc.cuda() # hack to get sampling on the GPU
        self.N.scale = self.N.scale.cuda()
        self.kl = 0

    def forward(self, x):
        #x = x.to(device)
        x = F.relu(self.conv1(x))
        x = F.relu(self.batch2(self.conv2(x)))
        x = F.relu(self.conv3(x))
        x = torch.flatten(x, start_dim=1)
        x = F.relu(self.linear1(x))
        mu =  self.linear2(x)
        sigma = torch.exp(self.linear3(x))
        z = mu + sigma*self.N.sample(mu.shape)
        self.kl = (sigma**2 + mu**2 - torch.log(sigma) - 1/2).sum()
        return z  

class Decoder(nn.Module):
    
    def __init__(self, latent_dims, num_channels, last_conv_size):
        super().__init__()

        self.decoder_lin = nn.Sequential(
            nn.Linear(latent_dims, 128),
            nn.ReLU(True),
            #nn.Linear(128, 3 * 3 * 32), # MNIST
            nn.Linear(128, last_conv_size * last_conv_size * 32),
            nn.ReLU(True)
        )

        self.unflatten = nn.Unflatten(dim=1, unflattened_size=(32, last_conv_size, last_conv_size))

        self.decoder_conv = nn.Sequential(
            nn.ConvTranspose2d(32, 16, 3, stride=2, output_padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(True),
            nn.ConvTranspose2d(16, 8, 3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(8),
            nn.ReLU(True),
            nn.ConvTranspose2d(8, num_channels, 3, stride=2, padding=1, output_padding=1)
        )
        
    def forward(self, x):
        x = self.decoder_lin(x)
        x = self.unflatten(x)
        x = self.decoder_conv(x)
        x = torch.sigmoid(x)
        return x


class VariationalAutoencoder(nn.Module):
    def __init__(self, latent_dims, num_channels=1, last_conv_size=3):
        super(VariationalAutoencoder, self).__init__()
        self.encoder = VariationalEncoder(latent_dims, num_channels, last_conv_size)
        self.decoder = Decoder(latent_dims, num_channels, last_conv_size)

    def forward(self, x):
        x = x.to(device)
        z = self.encoder(x)
        return self.decoder(z)


### Training function
def train_epoch(vae, device, dataloader, optimizer):
    # Set train mode for both the encoder and the decoder
    vae.train()
    train_loss = 0.0
    # Iterate the dataloader (we do not need the label values, this is unsupervised learning)
    for x, _ in dataloader: 
        # Move tensor to the proper device
        x = x.to(device)
        x_hat = vae(x)
        # Evaluate loss
        loss = ((x - x_hat)**2).sum() + vae.encoder.kl

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        # Print batch loss
        print('\t partial train loss (single batch): %f' % (loss.item()))
        train_loss+=loss.item()

    return train_loss / len(dataloader.dataset)

### Testing function
def test_epoch(vae, device, dataloader):
    # Set evaluation mode for encoder and decoder
    vae.eval()
    val_loss = 0.0
    with torch.no_grad(): # No need to track the gradients
        for x, _ in dataloader:
            # Move tensor to the proper device
            x = x.to(device)
            # Encode data
            encoded_data = vae.encoder(x)
            # Decode data
            x_hat = vae(x)
            loss = ((x - x_hat)**2).sum() + vae.encoder.kl
            val_loss += loss.item()

    return val_loss / len(dataloader.dataset)


def plot_ae_outputs(encoder,decoder,n=10):
    plt.figure(figsize=(16,4.5))
    t_idx = list(range(n))
    for i in range(n):
      ax = plt.subplot(2,n,i+1)
      img = test_dataset[t_idx[i]][0].unsqueeze(0).to(device)
      encoder.eval()
      decoder.eval()
      with torch.no_grad():
         rec_img  = decoder(encoder(img))
      plt.imshow(img.cpu().squeeze().permute([1,2,0]).numpy(), cmap='gist_gray')
      ax.get_xaxis().set_visible(False)
      ax.get_yaxis().set_visible(False)  
      if i == n//2:
        ax.set_title('Original images')
      ax = plt.subplot(2, n, i + 1 + n)
      plt.imshow(rec_img.cpu().squeeze().permute([1,2,0]).numpy(), cmap='gist_gray')  
      ax.get_xaxis().set_visible(False)
      ax.get_yaxis().set_visible(False)  
      if i == n//2:
         ax.set_title('Reconstructed images')
    #plt.show()


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
#from skimage.transform import resize
from IPython import embed
from sklearn.decomposition import PCA, IncrementalPCA
import torchvision.transforms as T
from PIL import Image
import socket
import os
import cloudpickle

GAME_SIZE = (420, 735, 3)
IMG_SIZE = 64

resize_for_vae = T.Compose([T.ToPILImage(),
                         T.Pad((np.max(GAME_SIZE[0:2]) - GAME_SIZE[1],
                                np.max(GAME_SIZE[0:2]) - GAME_SIZE[0])),
                         T.Resize((IMG_SIZE, IMG_SIZE), interpolation=Image.CUBIC),
                         T.ToTensor()])

def read_image_for_vae(path):
        img = cv2.imread(path)

        # from RC_RL::Player.get_screen()
        img = img.transpose((2, 0, 1))
        img = np.ascontiguousarray(img, dtype=np.float32) / 255
        img = torch.from_numpy(img)
        img = resize_for_vae(img)
        return img


class FramesDataset(Dataset):
    n_train = 430000
    n_test = 100 

    def __init__(self, rootDir, train):
        # from images_pca.py
        # first collect all images
        self.train = train
        self.all_frame_files = images_pca.get_all_frame_files(rootDir)
        random.shuffle(self.all_frame_files)
        self.all_frame_files = self.all_frame_files[:self.n_train+self.n_test]
        if self.train:
            self.all_frame_files = self.all_frame_files[:-self.n_test]
        else:
            self.all_frame_files = self.all_frame_files[-self.n_test:]

        img = cv2.imread(self.all_frame_files[0])
        self.game_size = img.shape
        assert self.game_size == GAME_SIZE
        self.img_size = IMG_SIZE

        # from RC_RL::Player.__init__()
        self.resize = T.Compose([T.ToPILImage(),
                                 T.Pad((np.max(self.game_size[0:2]) - self.game_size[1],
                                        np.max(self.game_size[0:2]) - self.game_size[0])),
                                 T.Resize((self.img_size, self.img_size), interpolation=Image.CUBIC),
                                 T.ToTensor()])


    def __len__(self):
        return len(self.all_frame_files)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        path = self.all_frame_files[idx]
        img = read_image_for_vae(path)
        #img = images_pca.process_frame(img, flatten=False)
        #img = img.transpose((2, 0, 1))
        return (img, 0) # artificial label



latent_dims = images_pca.n_components


if __name__ == '__main__':
    data_dir = 'dataset'

    rootDir = os.path.join(images_pca.imagesDir, 'DQN')
    frames_dataset = FramesDataset(rootDir, train=False)
    test_dataset = FramesDataset(rootDir, train=True)

    ## MIST
    #train_dataset = torchvision.datasets.MNIST(data_dir, train=True, download=True)
    #test_dataset  = torchvision.datasets.MNIST(data_dir, train=False, download=True)
    #transform = transforms.Compose([
    #    transforms.ToTensor(),
    #])
    #train_dataset.transform = transform
    #test_dataset.transform = transform


    #m=len(train_dataset)
    m=len(frames_dataset)

    #train_data, val_data = random_split(train_dataset, [int(m-m*0.2), int(m*0.2)])
    train_data, val_data = random_split(frames_dataset, [m - int(m*0.2), int(m*0.2)])
    batch_size = 256

    train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size)
    valid_loader = torch.utils.data.DataLoader(val_data, batch_size=batch_size)
    #test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=True) # MNIST
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=True)


    ### Set the random seed for reproducible results
    torch.manual_seed(0)

    #d = 4 # MNIST
    #vae = VariationalAutoencoder(latent_dims=d) # MNIST
    vae = VariationalAutoencoder(latent_dims=latent_dims, num_channels=3, last_conv_size=7)

    lr = 1e-3 

    optim = torch.optim.Adam(vae.parameters(), lr=lr, weight_decay=1e-5)

    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print(f'Selected device: {device}')

    vae.to(device)

    num_epochs = 1000


    train_losses = []
    val_losses = []
    for epoch in range(num_epochs):
       train_loss = train_epoch(vae,device,train_loader,optim)
       val_loss = test_epoch(vae,device,valid_loader)
       train_losses.append(train_loss)
       val_losses.append(val_loss)
       print('\n EPOCH {}/{} \t train loss {:.3f} \t val loss {:.3f}'.format(epoch + 1, num_epochs,train_loss,val_loss))
       plot_ae_outputs(vae.encoder,vae.decoder,n=10)
       plt.savefig('vae_test_e{}.png'.format(epoch+1))
       plt.close()



       filename = 'images_vae_epoch={}.pt'.format(epoch)
       filepath = os.path.join(images_pca.imagesDir, filename)
       print('saving to filepath: ', filepath)
       torch.save(vae, filepath)
       
       with open(os.path.join(images_pca.imagesDir, 'losses.pkl'), 'wb') as f:
           cloudpickle.dump({'train_losses': train_losses, 'val_losses': val_losses}, f, protocol=2)
