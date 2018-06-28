# this program combines all of the lesion pickles into one csv

import os
import sys
import pickle

rootdir = './lesions/exploration/'

outfile = open('all_pickles.csv', 'w')
outfile.write('gamename,step number,number of non-generic rules\n')

for subdir, dirs, files in os.walk(rootdir):
    # print subdir
    # print ''
    # print dirs
    # print ''
    if not dirs:
        # in the innermost file
        gamename = subdir[1+subdir.rfind('/'):]
        for file in files:
            print file
            # print os.path.join(subdir, file)
            theory = pickle.load(open(os.path.join(subdir, file), 'rb'))
            # theory.display()
            steps = int(file[:6])
            nongen = sum(0 if rule.generic else 1 for rule in theory.interactionSet)
            print gamename , steps , nongen
            outfile.write('{},{},{}\n'.format(gamename , steps , nongen))
outfile.close()