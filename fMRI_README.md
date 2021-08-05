Human vs. EMPA: fMRI Experimental Setup 
=======

This branch has code for human game play in an fMRI setting and EMPA theory induction based on replay of the human-generated state-action sequence.

Also see [resources](https://docs.google.com/document/d/1l9FNjAWZ5R8nJztV9XdIffFbE5X26x9kqAZ4JHUlV-s/edit) doc for pointers to other stuff.


Python setup
------

See README.md, though it's a bit incomplete. Here is how I got the code working on my Mac (in a virtual environment using [Anaconda](https://docs.anaconda.com/anaconda/install/mac-os/); make sure to install the Python 2.7 version; you might also need [Homebrew](https://brew.sh/)):

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

Also install the [SegoeUISymbol](https://freefontsdownload.net/free-segoeuisymbol-font-135679.htm) font; we use it to visualize symbols. Follow [guide](https://unix.stackexchange.com/questions/415246/how-to-install-fonts-for-centos-7/415249) for CentOS 7 for cluster. Or, just put .ttf file in local directory (already in repo, so should just work).

On NCF cluster, install conda using `module load` (see [CBS FAQ](http://cbs.fas.harvard.edu/science/core-facilities/neuroimaging/information-investigators/faq) and `module avail ncf`) and activate env with:

    source activate pedro


Mongo DB setup
------

We store all the experimental and behavioral data in [Mongo](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/). You need to have a local server working and the pymongo library installed.

Here is how I installed it on the lab Macbook Air:

    pip install pymongo
    pip install -r fmri_requirements.txt
    brew tap mongodb/brew
    brew install mongodb-community@4.2

    echo 'export PATH="/usr/local/opt/mongodb-community@4.2/bin:$PATH"' >> /Users/gershmanlab/.bash_profile

On NCF cluster, install using `module load`

Start Mongo server (don't mess with [ulimits](https://serverfault.com/questions/591812/how-to-set-ulimits-for-mongod)):

    mongod --config /usr/local/etc/mongod.conf --fork

Alternatively, to start automatically (on Mac):

    brew services start mongodb/brew/mongodb-community@4.2

Then test by connecting:

    mongo
    show dbs
    exit

To allow connections from other machines, set `bindIp` to `0.0.0.0` in `/usr/local/etc/mongod.conf`.

Then load the experiment db (dump is in the `dump` directory):

    mongorestore

Test it:

    mongo
    show dbs
    use heroku_7lzprs54
    show collections
    db.subjects.find({}, {subj_id: 1})

Should see `plays`, `subjects`, `regressors`, `runs`. Might have to clear them up:

    db.subjects.remove({})
    db.plays.remove({})
    db.runs.remove({})
    db.regressors.remove({})

Don't touch the `games` collection!

Depending on how old the dump is, might have to also do:

    db.plays.createIndex({ start_time: 1 })
    db.createCollection('plays_post')


To edit games, use the [jsVGDL](https://github.com/yl3506/heroku_vgdl) repo (ask Yichen for access) -- 
- Make sure in `app.js`, we are connecting to the local Mongo server (look for `mongoose.connect` around line 142, should connect to localhost)
- follow readme.txt to start NodeJS server (`npm start`)
- go to `http://127.0.0.1:3000/admin` (p: cocosciiscool) to edit games (prefix `vgfmri3_`)
- as sanity check, maybe stop mongo server and make sure it stops working (so we don't accidentally end up editing live games for the online experiment)


On NCF cluster, start it on an interactive node (make sure to create appropriate directory with `mongod.conf`, which should also be configured properly -- see `mongod-ncf.conf` in this repo):

    mongod --config /ncf/gershman/Lab/scripts/VGDL/mongodb/mongod.conf --fork 

Test with `ps aux | grep mongo`. Type `hostname` in command line to figure out hostname and use it to connect to it from other nodes and jobs.

Btw seems like the `ncf` and `ncf_interact` nodes are on a different network from the `ncflogin` and `ncfood` (VDI) nodes, so you probs need to run a separate mongo instance there, e.g. to generate the videos:

    mongod --config /ncf/gershman/Lab/scripts/VGDL/mongodb_2/mongod_2.conf --fork 

Then `mongodump` from a `ncf_interact` node and then `mongorestore` on the VDI node.


On Cannon cluster, create [VDI node](https://vdi.rc.fas.harvard.edu/pun/sys/dashboard/batch_connect/sessions) (make sure to connect to the VPN with @fasrc or @odyssey; then select FAS-RC remote desktop, 28 day, 20 GB) and start with:

    mongod --config /n/gershman_lab/users/mtomov13/mongo/mongod.conf


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

Might have to clear collections if re-running the same run, (it will just add more play TODO fix).

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

    rm savedCurricula/*; python fmri_empaPlay.py 0 0 0 0 0

Note that this is generative play, that is, EMPA is playing the same levels in the same order as the subject, but it is choosing its own actions and hence the state sequence will diverge from that of the human.

This is useful for making sure EMPA can play the games and learn the theory.

Also saves a video file in `videos/`.

Might have to clear `savedCurricula` if re-running the same run / play.


fMRI EMPA Replay
-----

To have EMPA replay the human state-action sequence and learn a theory (as if it was playing), do:

    python fmri_empaReplay.py [subj_id] [run_id] [block_id*] [instance_id*] [play_id*]

E.g.

    rm savedCurricula/*; python fmri_empaReplay.py 0 0
        
This will be used to generate independent variables for the fMRI analysis. The idea is that, if humans have something like EMPA in their heads, then they should be inferring theories like those that EMPA would infer. 

It is important for EMPA to learn using the same state-action sequence as the humans -- otherwise, it might experience a totally different sequence of events and hence infer a totally different sequence of theories. Even if the asymptotic theory might be the same as that inferred by the human, the intermediate theories (which we will be using to analyze the brain data) will not.


On the cluster: need to hack the `uuid` library. Run `source activate pedro` (assuming you've already created it as described above) and run in `ipython`:

    import uuid
    print uuid.__file__

Then open the file (the .py, not .pyc file) and somewhere after line 487 add:

    # momchil: b/c we had ppl play on Mac, there is a mismatch between this and the cluster
    # on the Mac, when new sprites are created (e.g. on lemmings), _uuid_generate_time = None (see above)
    # and uuid1() uses random to generate the UUIDs;
    # on the cluster, _uuid_generate_time is not None, so we don't call random
    # this results in a mismatch between action replay on the cluster vs. the Mac, which expects the exact same
    # sequence of calls to random during sprite updates
    _uuid_generate_time = None # TODO momchil hack


Other scripts
----

`fmri_makeMovie.py` -- create movies with EMPA replay after running fmri_empaReplay; run it in an browser [interactive session](https://ncfoodnode02.rc.fas.harvard.edu/pun/sys/dashboard/batch_connect/sessions) (need VPN), on a Cannon Compute node (need memory -- 50 G)

`fmri_playsPostproc.py` -- generate nuisance regressors for GLMs


Tips & Gotchas
-----

To see where you `embed()`ed, do:

    import sys, traceback
    traceback.print_stack()

Python time profiling: [cProfile](https://stackoverflow.com/questions/582336/how-can-you-profile-a-python-script), e.g. `python -m cProfile -s cumtime fmri_empaReplay.py 1 0 0 0 0 > chase_profile.txt`

Python memory profiling: [memory-profiler](https://pypi.org/project/memory-profiler/), or `get_size` in `utils.py`

Careful not to overwrite local scp\*.sh files when copying from NCF

Careful not to overwrite remote theory_files when copying to NCF

Careful not to edit .py files while scripts are running; they might use the latest version

EMPA replay checklist
-----

Before running `fmri_empaReplay.sh`, make sure to check:
- `run_fmri_empaReplay.sh`: `rm savedCurricula/*` if replaying from scratch (or not, if we're continuing replay)
- `fmri_empaReplay.sh`: subjects, games, memory, time limit (start small, e.g. subj 1 chase only)
- `mongo`: `db.regressors.remove({})` (dump first, tar gzip and mv to `../backups`)
- `fmri_empaReplay.py`: `db.regressors.insert` and `continue` are uncommented


EMPA postprocessing checklist 
-----

Before running `fmri_playsPostproc.sh`, make sure to:
- `python fmri_countRegressors.py [subj]` for all subjects, make sure everything is good
- `mongodump` remotely
- `tar -zcvf dump_DATE_DECS.tar.gz dump`, `mv dump_DATE_DESC.tar.gz ../backups`
- `scp_from_ncf.sh` edit and copy over regressors jsons (make sure the ones you have already are archived locally)
- `mongo`: `db.plays_post.remove({})`
- `fmri_playsPostproc.py`: `db.plays_post.insert` and `continue` are uncommented


EMPA GLMs
-----

Before running GLMs:
- `mongodump`, tar gzip, mv to backups
- `scp_from_ncf.sh` edit and copy over `plays_post` jsons (make sure the ones you have already are archived locally)
- zip
- `mongo`: `db.regressors.remove({})`, `db.plays_post.remove({})`
- `mongorestore`
- (in `matlab_vgdl`) `rm mat/get_*.mat`, `rm mat/*create_multi*.mat`
- run `get_regressors` as script (comment out first line, uncomment stuff right after) to debug
- (MATLAB) `ccnl_check_multi(vgdl_expt(), 3)` to get theory regressors, then 21 to get everything else
- `ccnl_check_multi` for all GLMs you intend to run, then `scp_to_ncf.sh` to copy them over (edit first)


HRR GP analysis
-----

- run `fmri_empaReplay.py` / `fmri_empaReplay.sh`: human play -> EMPA theories
    - EMPA generates theory sequence from human replay
    - saves it to mongo (metadata in `regressors` collection), disk (`theories/theory_*.pickle`)

- run `HRR.py`: `gen_and_save_subject_kernels_batched` / `HRR.sh`: EMPA theories -> HRR embeddings -> kernel (nTRs x nTRs)
    - (edit `__main__`)
    - generates subject-specific HRRs (multiple samples)
    - embeds EMPA theory sequence
    - computes kernel for GP
    - saves to disk (`mat/HRR_subject_kernel_*.mat`)

- (in [MATLAB repo](https://github.com/tomov/VGDL-fMRI-Data-Analysis)) run `fit_gp_CV.m` / `fit_gp_CV.sh`: kernel -> predicted BOLD <-> actual BOLD
    - (make sure to cp mat file to `mat_vgdl` dir / mat/)
    - (edit `filename` if necessary)
    - fits GP to BOLD and evaluates fit in each voxel
    - saves to disk (`mat/fit_gp_CV_*.mat`)

- run `agg_gp_CV.m`, then `plot_gp_CV.m`: visualize results
    - (edit file to load from `fit_gp_CV` results)
    - (edit `filename` if necessary)



Decoding HRR GP
-----

- run GP analysis first (see above): human play -> EMPA theories

- run `HRR.py`: `gen_and_save_subject_unique_HRRs` / `HRR.sh`: EMPA theories -> HRR embeddings
    - (edit `__main__`)
    - generates subject-specific HRRs (multiple samples)
    - embeds EMPA theories (only unique ones)
    - saves HRRs to disk (`mat/unique_HRR_subject_*.mat`)
    - saves theories to disk (`theories/unique_theories_subject_*.pickle`)

- (in [MATLAB repo](https://github.com/tomov/VGDL-fMRI-Data-Analysis)) run `decode_gp_CV.m` / `decode_gp_CV.sh`: BOLD -> decoded theories
    - generates EMPA theory sequence that better fits the BOLD than the original EMPA theory sequence
    - saves to disk (`mat/decode_gp_CV_*.mat`)

- run `fmri_empaTheoryReplay.py`: theories -> subject behavior, EMPA (predicted) behavior

- run `fmri_empaLik.py`: subject, EMPA behavior -> likelihood
