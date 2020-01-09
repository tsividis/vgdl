Human vs. EMPA: fMRI Experimental Setup 
=======

This branch has code for human game play in an fMRI setting and EMPA theory induction based on replay of the human-generated state-action sequence.


Python setup
------

See README.md, though it's a bit incomplete. Here is how I got the code working on my Mac (in a virtual environment using [Anaconda](https://docs.anaconda.com/anaconda/install/mac-os/); make sure to install the Python 2.7 version):

    conda deactivate
    conda create -n pedro python=2
    conda activate pedro

    brew install ffmpeg

    python -m pip install -U pygame --user
    python -m pygame.examples.aliens

    pip install numpy
    pip install scipy
    pip install IPython line_profiler ipdb
    python -m examples.gridphysics.aliens

The [PyGame](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/) guide might also be helpful.


Mongo DB setup
------

We store all the experimental and behavioral data in [Mongo](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/). You need to have a local server working and the pymongo library installed.

Here is how I installed it on my Mac:

    pip install pymongo
    pip install fmri_requirements.txt
    brew install mongo

Then load the experiment db:

    mongorestore


fMRI Human Play 
-----

Run the fMRI experiment with:

    python fmri_play.py [subj_id] [run_id]

E.g.

    python fmri_play.py 0 0

This fetches the pre-generated experimental protocol (sequence of game instances) for the given subject from the db, lets the subject play the games, and records all actions, events, and game states in the db. If no experimental protocol exists for the given subject, it is generated and saved to the db.

This always executes the same sequence of game instances for a given subject-run pair.
There are three reasons for this:

1. Verification: fMRI experiments are expensive and time-consuming, and generating the protocol on-the-fly (as we usually do for web experiments) is error-prone. By pre-generating the protocol for each subject, we can a) manually inspect it and make sure all conditions are present, randomized properly, etc., and b) actually try it out to make sure the subjective experience is acceptable (e.g. not too many key presses, etc.)

2. Restarting: the scanner or the experimental computer sometimes crash. This means we should be able to restart the experiment from the next run (we just discard the run that crashed). To do this, we need to have pre-generated the protocol for all runs (to ensure counter-balancing of conditions across runs, etc.).

3. Debugging: it is easier to reproduce a bug if the game sequence is deterministic.

Find the experimental protocol [here](https://docs.google.com/presentation/d/1IKguSLIAd5SXZ5dM4N86EFgwlU-0ROCBQEmiEtJxcrc/edit#slide=id.g6b95b53d30_1_65).
- Each _subject_ will have 6 _runs_ (1 run = 1 scanner session).
- Each _run_ has 3 _blocks_ of 3 _instances_ (game levels) each.
- Each _instance_ corresponds to a game level which the subject plays on repeat (multiple _plays_) for 1 min total. This is necessary because we want the same amount of fMRI data for each game, but subjects might finish some instances faster than others.


fMRI Human Replay
-----

Generate a video for a given fMRI run with:

    python fmri_replay.py [subj_id] [run_id] [block_id*] [instance_id*] [play_id*]

E.g.

    python fmri_replay.py 0 0

Then find video file in `videos/`. The * means optional; if omitted, it will include all of them.

This is useful for making sure the state sequence is logged properly in the db.

A MATLAB script to sanity check event times can be found [here](https://github.com/tomov/VGDL-fMRI-Data-Analysis/blob/d8064a7038238ceac631d49360b6d9216eda6d0d/viz_events.m)


fMRI EMPA Play
-----

To have EMPA play the same sequence of game instances as the subject, do:

    python fmri_empaPlay.py [subj_id] [run_id] [block_id*] [instance_id*] [play_id*]

E.g.

    python fmri_empaPlay.py 0 0

Note that this is generative play, that is, EMPA is playing the same levels in the same order as the subject, but it is choosing its own actions and hence the state sequence will diverge from that of the human.

This is useful for making sure EMPA can play the games and learn the theory.

Also saves a video file in `videos/`.


fMRI EMPA Replay
-----

To have EMPA replay the human state-action sequence and learn a theory (as if it was playing), do:

    python fmri_empaReplay.py [subj_id] [run_id] [block_id*] [instance_id*] [play_id*]

E.g.

    python fmri_empaReplay.py 0 0
        
This will be used to generate independent variables for the fMRI analysis. The idea is that, if humans have something like EMPA in their heads, then they should be inferring theories like those that EMPA would infer. 

It is important for EMPA to learn using the same state-action sequence as the humans -- otherwise, it might experience a totally different sequence of events and hence infer a totally different sequence of theories. Even if the asymptotic theory might be the same as that inferred by the human, the intermediate theories (which we will be using to analyze the brain data) will not.

TODO

Currently, this is broken.
