import games_to_hyperparameters, os, itertools, subprocess, shlex, psutil, time
from joblib import Parallel, delayed

num_cores = psutil.cpu_count()

lst = []
for k,v in params.games_to_hyperparameters.items():
	x = itertools.repeat(k)
	lst.extend(zip(x,v))

def run_models(game_name, hyperparam_index):
	call_string = "python -m vgdl.load_games --game_name {} --hyperparam_index {}".format(game_name, hyperparam_index)
	# time.sleep(10)
	# call_string = "echo \"{} {}\"".format(game_name, hyperparam_index)
	subprocess.call(shlex.split(call_string))

Parallel(n_jobs=num_cores)(delayed(run_models)(game_name, hyperparam_index) for game_name, hyperparam_index in lst)
