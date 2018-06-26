
# game_names = ['expt_antagonist', 'expt_helper', 'expt_push_boulders', #0-3 'expt_preconditions',

#                 'aliens', 'boulderdash', 'butterflies', 'chase', 'frogs',                   #5-8
#                 'missilecommand', 'portals', 'sokoban', 'survivezombies',                   #9-12
#                 'zelda',                                                                    #13
                    
#                 'angelsdemons', 'avoidgeorge', 'bait', 'boulderchase',                      #14-17
#                 'camelRace', 'chopper', 'clusters', 'cookmepasta',                          #18-21
#                 'infection', 'jaws', 'lemmings', 'modality',                                #22-25
#                 'myAliens', 'overload', 'plants', 'plaqueattack',                           #26-29
#                 'shipwreck','superman', 'tercio', 'thesnowman',                             #30-33
#                 'watergame', 'waves', 'wildgunman']                                         #34-36

# game_names = ['expt_push_boulders', 'aliens', 'butterflies', 'expt_helper', 'frogs', 'portals', 'survivezombies', 'zelda']
# game_names = ['boulderchase', 'jaws', 'myAliens', 'overload', 'avoidgeorge']

##running with hyperparams2
# game_names = ['avoidgeorge', 'bait', 'boulderchase', 'chopper', 'clusters',
# 				jaws', 'lemmings',
# 				'myAliens', 'overload', 'plants', 'plaqueattack', 
# 				'superman', 'watergame', 'waves', 'wildgunman']

## running with hyperparams2
game_names = ['bait', 'clusters']

## running with hyperparams3
# game_names = ['myAliens'] ##running for longer
# game_names = ['chopper', 'jaws', 'plaqueattack', 'wildgunman']
# game_names = ['avoidgeorge', 'bait', 'chopper', 
# 				'infection', 'jaws', 'myAliens', 'overload', 'plants', 'plaqueattack', 
# 				'superman', 'waves', 'wildgunman']

## to run after local debugging:
# ['boulderchase']
mapping = dict()

# for k in game_names:
#     if k not in ['infection', 'lemmings', 'modality', 'plants', 'tercio', 'waves']: #[need much looking into]
#         mapping[k] = [0,2,3]

for k in game_names:
    mapping[k] = [3]