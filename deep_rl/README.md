# Spatial Reasoning

Change the game name in [utils/options.py](utils/options.py#L18):

`[ "dqn",      "vgdl",      "portals",                  "dqn-cnn",      "sequential"],`

and then run
`python main.py`

(You might also want to change the training signature to keep track of your runs.)

## Installation
[PyTorch](http://pytorch.org/) and the rest of the VGDL requirements.

## Known Issues
`pygame.init()` seems to be initializing something audio related in the background, which might give warnings based on permissions on OpenMind. [Here](https://stackoverflow.com/questions/31847497/pygame-tries-to-use-alsa?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa) is a description of the warning. This doesn't affect performance, but might make viewing your results a little harder depending on if the warnings get recorded in your logs. 

## Misc
The default implementation of the DQN downsamples screen sizes to ~42x42 and converts them to greyscale. I kept the downsampling, but not the greyscale conversion. Look at [examples/] for a raw and processed image to get a sense of what the network inputs look like, and let me know if you would like a different preprocessing.
