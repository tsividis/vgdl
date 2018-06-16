from collections import defaultdict

game_names = ['angelsdemons', 'avoidgeorge', 'bait', 'boulderchase', \
             'boulderdash', 'butterflies', 'camelRace', 'chase', \
             'chopper', 'clusters', 'cookmepasta', 'infection',\
             'jaws', 'lemmings', 'modality', 'myAliens',\
             'overload', 'plants', 'plaqueattack', 'shipwreck',\
             'superman', 'tercio', 'thesnowman', 'tiny_game1', 'tiny_game2',\
             'watergame', 'waves', 'wildgunman']

mapping = dict()

for k in ['angelsdemons', 'avoidgeorge']:
    mapping[k] = [0,2]
