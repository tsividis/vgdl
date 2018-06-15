import params, os, itertools, subprocess, shlex, psutil, time
from joblib import Parallel, delayed

num_cores = psutil.cpu_count()
print num_cores
lst = []
for k,v in params.games_to_hyperparameters.items():
	x = itertools.repeat(k)
	lst.extend(zip(x,v))

def run_models(game_name, hyperparams):
	# call_string = "python -m vgdl.parallel_planning --game_name {} --hyperparams {}".format(game_name, hyperparams)
	time.sleep(10)
	call_string = "echo \"{} {}\"".format(game_name, hyperparams)
	subprocess.call(shlex.split(call_string))

Parallel(n_jobs=num_cores)(delayed(run_models)(game_name, hyperparams) for game_name, hyperparams in lst)
