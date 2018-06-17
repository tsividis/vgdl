from collections import defaultdict

game_names = ['angelsdemons', 'avoidgeorge', 'bait', 'boulderchase', \
             'boulderdash', 'butterflies', 'camelRace', 'chase', \
             'chopper', 'clusters', 'cookmepasta', 'infection',\
             'jaws', 'lemmings', 'modality', 'myAliens',\
             'overload', 'plants', 'plaqueattack', 'shipwreck',\
             'superman', 'tercio', 'thesnowman', \
             'watergame', 'waves', 'wildgunman']

mapping = dict()

for k in game_names:
    if k not in ['lemmings', 'plants', 'shipwreck', 'waves']: # ignore these for now
        mapping[k] = [0,2]
