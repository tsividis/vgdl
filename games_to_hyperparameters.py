
# game_names = ['expt_antagonist', 'expt_helper', 'expt_push_boulders', #0-3 'expt_preconditions',

#                 'aliens', 'boulderdash', 'butterflies', 'chase', 'frogs',                   #5-8
#                 'missilecommand', 'portals', 'sokoban', 'survivezombies',                   #9-12
#                 'zelda',                                                                    #13
                    
#                 'angelsdemons', 'avoidgeorge', 'bait', 'boulderchase',                      #14-17
#                 'camelRace', 'chopper', 'clusters', 'cookmepasta',                          #18-21
#                 'jaws', 'lemmings', 'modality', 'myAliens',                                 #22-25
#                 'overload', 'plants', 'plaqueattack',  'shipwreck',                         #26-29
#                 'superman', 'tercio', 'thesnowman', 'watergame',                            #30-33
#                 'waves', 'wildgunman']                                         		      #34-36

# game_names = ['aliens', 'butterflies', 'expt_helper', 'expt_push_boulders', 'frogs', 'portals', 'survivezombies', 'zelda']

# game_names = [ 'expt_helper', 'expt_push_boulders', 'zelda', 'angelsdemons', 'avoidgeorge', 
# 			'bait', 'camelRace', 'chopper', 'clusters',
# 			'jaws', 'lemmings', 'myAliens', 'overload', 'plants', 
# 			'plaqueattack', 'shipwreck','superman','watergame', 'waves',
# 			 'wildgunman', 'aliens', 'boulderchase', 'modality', 'tercio']

game_names = ['lemmings', 'expt_helper']
#skipped: , cookmepasta, thesnowman, shipwreck
# run w/ different params: boulderchase, modality, tercio


mapping = dict()

for k in game_names:
    if k in ['aliens', 'myAliens']:
        mapping[k] = [2,3]
    else:
    	mapping[k] = [2]


# for k in game_names:
#     mapping[k] = [2]