from collections import defaultdict

game_names = ['aliens', 'angelsdemons', 'avoidgeorge', 'bait', 'boulderchase', \
             'boulderdash', 'butterflies', 'camelRace', 'chase', \
             'chopper', 'clusters', 'cookmepasta', 'frogs', 'infection',\
             'jaws', 'lemmings', 'modality', 'myAliens',\
             'overload', 'plants', 'plaqueattack', 'shipwreck',\
             'superman', 'tercio', 'thesnowman', \
             'watergame', 'waves', 'wildgunman']

mapping = dict()

# for k in game_names:
#     if k not in ['aliens', 'boulderdash', 'butterflies', 'chase', 'frogs', 'missilecommand', 'portals', 'sokoban', 'survivezombies', 'zelda']+\
#                     ['infection', 'lemmings', 'modality', 'plants', 'tercio', 'waves']: #[need a little debugging] [need much looking into]
#         mapping[k] = [0,2,3]

for k in ['aliens', 'boulderdash', 'butterflies', 'chase', 'frogs', 'missilecommand', 'portals', 'sokoban', 'survivezombies', 'zelda']:
    mapping[k] = [2]