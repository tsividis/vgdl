# structural equation modeling to discover functional connectivity
# data generated with get_betas_for_tetrad.m in MATLAB

# install with (need python 3.7+):
# pip install semopy==2.0.0a4
# follow http://semopy.com/tutorial.html not https://pypi.org/project/semopy/

# old:
# had to vi ~/anaconda3/lib/python3.7/site-packages/semopy/model_base.py 
# and sys.path.append('/Users/momchil/anaconda3/lib/python3.7/site-packages/semopy')
# and also rename parser.py to e.g. parser_sem.py and import it like that...
from semopy import Model
from semopy import stats
import numpy as np
import os
import pandas as pd
from IPython import embed
import scipy.io
from scipy.stats import wishart


names = ['top_down', 'bottom_up']

descs_confirm = [
        # tetrad IMAGES winner for GLM 109 beta series (@ theory updates)
         """ SMA ~ SFG + MFG + IFGoperc + IFGtriang + SOG
             SOG ~ MOG
             MOG ~ SFG + IFGoperc
             FFG ~ IFGtriang + IFGoperc + SOG + IOG
             LING ~ MOG + SOG + FFG + IOG
             IOG ~ MOG + IFGoperc
             CUN ~ CAL + SOG + MOG + FFG
             CAL ~ SOG + LING + FFG
         """,
        # tetrad IMAGES winner for GLM 120 beta series (@ theory updates + 2s)
         """ SMA ~ SFG + MFG + IFGoperc
             SFG ~ MFG
             MFG ~ SOG + IFGoperc
             IFGoperc ~ FFG + IOG
             IFGtriang ~ MFG + IFGoperc + SFG + SMA + CUN
             SOG ~ IFGoperc + MOG + IOG + CUN
             IOG ~ FFG + MOG + LING + CUN
         """,
         ]



def gen_descs_helper(cur, cand, ix, descs):

    if ix == len(cand):
        desc = ''
        for k, v in cur.items():
            desc += k + ' ~ ' + ' + '.join(v) + '   \n'

        #if 'Ins' in cur['IFG'] and 'IFG' in cur['Ins']:
        #    return # TODO hack ensure DAG
        descs.append(desc)
        return

    # without A -> B
    gen_descs_helper(cur, cand, ix + 1, descs)

    A = cand[ix][0]
    B = cand[ix][1]
    cur[B].append(A)
    # with A -> B
    gen_descs_helper(cur, cand, ix + 1, descs)
    cur[B].remove(A)

def gen_descs(base, cand):
    descs = []
    gen_descs_helper(base, cand, 0, descs)
    return descs

base = {'Put': ['RPEpsi'], 'VS': ['RPE'], 'IFG': ['psi'], 'Ins': ['psi']}
cand = [('Ins', 'Put'), ('IFG', 'Put'), ('VS', 'Put'), ('IFG', 'Ins'), ('Ins', 'IFG')]

# auto generate models
#
#descs = gen_descs(base, cand)

#print(descs)
#embed()



descs = descs_confirm



for dirname in ['GLM_109', 'GLM_120']:

    print(dirname)

    files = os.listdir(os.path.join('tetrad', dirname))
    files = [f for f in files if f.endswith('.txt') ]

    n_subjects = len(files) # num subjects
    n_models = len(descs) # num models

    logliks = np.zeros((n_subjects, n_models)) # likelihoods
    lmes = np.zeros((n_subjects, n_models)) # LMEs = -0.5 * BICs
    bics = np.zeros((n_subjects, n_models)) # BICs
    ks = np.zeros((n_subjects, n_models)) # # params
    ns = np.zeros((n_subjects, n_models)) # # data points

    for i in range(n_subjects):

        for j in range(n_models):

            model = Model(descs[j])

            filepath = os.path.join(dirname, files[i])
            data = pd.read_csv(filepath, sep='\t')

            opt_res = model.fit(data)

            # from /Users/momchil/anaconda3/lib/python3.7/site-packages/semopy/stats.py: calc_bic()
            # WARNING: all of these are up to a proportionality constant that DIFFERS ACROSS SUBJECTS => do not use for BMS
            #
            '''
            logliks[i,j] = stats.calc_likelihood(model) # note up to proportionality constant, b/c w.r.t. saturated model, but that's the same for all models so it's fine
            ks[i,j], ns[i,j] = len(model.param_vals), model.mx_data.shape[0]
            bic = stats.calc_bic(model)
            lmes[i,j] = -0.5 * bic
            '''

            # calculate likelihood manually, following https://en.wikipedia.org/wiki/Wishart_distribution
            # and https://math.stackexchange.com/questions/2803164/degrees-of-freedom-in-a-wishart-distribution
            # and /Users/momchil/anaconda3/lib/python3.7/site-packages/semopy/stats.py: obj_mlw()
            # and /Users/momchil/anaconda3/lib/python3.7/site-packages/semopy/stats.py: calc_bic()
            # and /Users/momchil/anaconda3/lib/python3.7/site-packages/semopy/stats.py: calc_likelihood()
            model.update_matrices(model.param_vals)
            S = model.mx_cov # empirical covariance matrix
            sigma, _ = model.calc_sigma() # model covariance matrix
            p = sigma.shape[0] # # of variables
            n = model.mx_data.shape[0] # dof = # of data points (b/c Wishart is generalization of Chi2 to MVN => sum of n squared i.i.d. MVNs)
            k = len(model.param_vals) # # of free params

            loglik = wishart.logpdf(S, df=n, scale=sigma)
            bic = k*np.log(n) - 2*loglik
            lme = -0.5 * bic 

            logliks[i,j] = loglik
            ks[i,j] = k 
            ns[i,j] = n
            bics[i,j] = bic 
            lmes[i,j] = lme

            print('subj=', i, ' mod=', j, filepath, ' k=', k, ' n=', n, ' loglik=', logliks[i,j])
            print(model.mx_cov.shape)

    print(lmes.shape)

    d = {'lmes': lmes,
         'bics': bics,
         'logliks': logliks,
         'ks': ks,
         'ns': ns,
         'files': files,
         'descs': descs}

    filename = 'mat/semopy_%s_lmes.mat' % dirname
    print(filename)
    scipy.io.savemat(filename, d)



