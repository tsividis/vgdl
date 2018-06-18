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
    if k not in ['boulderdash', 'butterflies', 'chase']+['bait', 'jaws', 'myAliens', 'shipwreck', 'plaqueattack', 'wildgunman']+['infection', 'lemmings', 'modality', 'plants', 'tercio', 'waves']: #[need a little debugging] [need much looking into]
        mapping[k] = [0,2]

# for k in ['avoidgeorge', 'bait']:
    # mapping[k] = [0,2]