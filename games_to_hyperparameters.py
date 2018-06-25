
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
game_names = ['aliens', 'butterflies']
mapping = dict()

# for k in game_names:
#     if k not in ['infection', 'lemmings', 'modality', 'plants', 'tercio', 'waves']: #[need much looking into]
#         mapping[k] = [0,2,3]

for k in game_names:
    mapping[k] = [3]