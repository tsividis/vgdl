# 
# game_names = ['expt_antagonist', 'expt_helper', 'expt_push_boulders',	'expt_preconditions',					  #0-3
#                 'aliens', 'boulderdash', 'butterflies', 'chase', 'frogs',                   #5-8
#                 'missilecommand', 'portals', 'sokoban', 'survivezombies',                   #9-12
#                 'zelda',                                                                    #13
                    
#                 'avoidgeorge', 'bait', 'boulderchase',                   #14-17
#                 'camelRace', 'chopper', 'jaws', 'lemmings', 'myAliens',		                     	 #18-21
#                  'overload', 'plaqueattack','watergame',	    		 #22-25
#                  'waves']                               	 #26-27


## low memory
# game_names = ['aliens', 'butterflies', 'chase', 'missilecommand', 'survivezombies', 'zelda', 'camelRace', 'lemmings', 'myAliens', 'plaqueattack',
			 # 'frogs', 'expt_ee','expt_push_boulders', 'sokoban', 'd2']

## more memory
game_names = ['avoidgeorge', 'expt_antagonist', 'expt_helper', 'expt_preconditions', 'expt_relational', 'jaws', 'boulderdash', 'portals']
# game_names = ['watergame', 'bait']
##low-memory games where position_score seems to affect results
# game_names = ['avoidgeorge', 'med_boulderdash', 'survivezombies', 'zelda', 'frogs']
##high-memory games where position_score seems to affect results
# game_names = ['expt_relational', 'jaws', 'watergame', 'bait', 'portals']

# game_names = ['zelda', 'bait']

# game_names = ['expt_helper']

## idx 1:
# game_names = ['expt_push_boulders', 'portals', 'frogs', 'overload', 'expt_antagonist', 'expt_helper'] 

## idx 2:
# game_names = ['expt_push_boulders', 'portals', 'frogs', 'overload', 'expt_antagonist', 'expt_helper'] #boulderdash, boulderchase

## idx 2, skip induction (for now):
# game_names = ['expt_push_boulders', 'expt_preconditions', 'sokoban', 'bait', 'watergame']

## idx 2, normal
# game_names = ['expt_antagonist', 'expt_helper', 'portals', 'med_boulderdash']

# ## idx 3
# game_names = ['frogs']
# game_names = ['aliens', 'avoidgeorge', 'butterflies', 'chase', 'missilecommand', 'survivezombies', 'zelda', 'camelRace', 'jaws', 'lemmings', 'myAliens', 'overload', 'plaqueattack', 'waves', 'frogs', 'portals']
# game_names = ['survivezombies', 'jaws']
# game_names = ['chopper', 'plaqueattack']
# game_names = ['zelda', 'jaws', 'waves', 'survivezombies']

# ## idx 3, more memory
# game_names = ['chopper']

# game_names = ['expt_push_boulders', 'aliens', 'butterflies', 'expt_helper', 'frogs', 'portals', 'survivezombies', 'zelda']
# game_names = ['boulderchase', 'jaws', 'myAliens', 'overload', 'avoidgeorge']

##running with hyperparams2
# game_names = ['avoidgeorge', 'bait', 'boulderchase', 'chopper', 'clusters',
# 				jaws', 'lemmings',
# 				'myAliens', 'overload', 'plants', 'plaqueattack', 
# 				'superman', 'watergame', 'waves', 'wildgunman']

## running with hyperparams2
# game_names = ['bait', 'camelRace', 'lemmings', 'watergame','boulderchase', 'boulderdash']

## running with hyperparams3
# game_names = ['myAliens'] ##running for longer
# game_names = ['avoidgeorge', 'jaws','boulderchase', 'boulderdash', 'chopper', 'myAliens', 'plaqueattack', 'waves', 'overload', 'missilecommand', 'lemmings', 'superman']
# game_names = ['avoidgeorge', 'bait', 'chopper', 
				# 'infection', 'jaws', 'myAliens', 'overload', 'plants', 'plaqueattack', 
				# 'superman', 'waves', 'wildgunman']

# game_names = ['angelsdemons', 'waves', 'myAliens', 'jaws']

## to run after local debugging:
# ['boulderchase']
# mapping = dict()

# for k in game_names:
#     if k not in ['infection', 'lemmings', 'modality', 'plants', 'tercio', 'waves']: #[need much looking into]
#         mapping[k] = [0,2,3]

# for k in game_names:
    # mapping[k] = [3]
