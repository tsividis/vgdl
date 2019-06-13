
# # low memory -- 16gb
# game_names = ['aliens', 'variant_aliens_1', 'variant_aliens_2', 'variant_aliens_3', 'variant_aliens_4', 
# 'avoidgeorge', 'variant_avoidgeorge_1', 'variant_avoidgeorge_2', 'variant_avoidgeorge_3', 'variant_avoidgeorge_4',
# 'bait', 'variant_bait_1', 'variant_bait_2',
# 'bees_and_birds','variant_bees_and_birds_1',  
# 'butterflies', 'variant_butterflies_1', 'variant_butterflies_2', 
# 'boulderdash', 'variant_boulderdash_1', 'variant_boulderdash_2',
# 'chase', 'variant_chase_1', 'variant_chase_2', 'variant_chase_3', 
# 'closing_gates', 'variant_closing_gates_1',
# 'corridor','variant_corridor_1', 
# 'expt_antagonist', 'variant_expt_antagonist_1','variant_expt_antagonist_2', 
# 'expt_ee', 'variant_expt_ee_1', 'variant_expt_ee_2', 'variant_expt_ee_3', 
# 'expt_helper', 'variant_expt_helper_1', 'variant_expt_helper_2', 
# 'expt_preconditions', 'variant_expt_preconditions_1', 'variant_expt_preconditions_2',
# 'expt_push_boulders', 'variant_expt_push_boulders_1', 'variant_expt_push_boulders_2', 
# 'expt_relational', 'variant_expt_relational_1', 'variant_expt_relational_2',
# 'frogs', 'variant_frogs_1', 'variant_frogs_2', 'variant_frogs_3',
# 'jaws', 'variant_jaws_1', 'variant_jaws_2',
# 'lemmings', 'variant_lemmings_1',  'variant_lemmings_2', 'variant_lemmings_3',
# 'missilecommand', 'variant_missilecommand_1', 'variant_missilecommand_2', 'variant_missilecommand_3', 'variant_missilecommand_4',
# 'myAliens', 'variant_myAliens_1', 'variant_myAliens_2',
# 'plaqueattack', 'variant_plaqueattack_1', 'variant_plaqueattack_2', 'variant_plaqueattack_3',
# 'portals', 'variant_portals_1', 'variant_portals_2',
# 'surprise', 'variant_surprise_1', 'variant_surprise_2',
# 'survivezombies', 'variant_survivezombies_1', 'variant_survivezombies_2',
# 'sokoban', 'variant_sokoban_1', 'variant_sokoban_2',
# 'watergame', 'variant_watergame_1', 'variant_watergame_2',
# 'zelda','variant_zelda_1', 'variant_zelda_2', 'variant_zelda_3'] #90 total


### no subgoals, no gradients, no IW
### 10x
# game_names = ['variant_bees_and_birds_1', 'variant_closing_gates_1', 'butterflies', 'chase', 'missilecommand', 'variant_butterflies_2', 'variant_chase_1', 
# 'variant_expt_antagonist_1', 'variant_expt_antagonist_2', 'variant_expt_ee_2', 'variant_expt_preconditions_1', 'variant_expt_preconditions_2',
# 'variant_expt_push_boulders_1', 'variant_expt_push_boulders_2', 'variant_expt_relational_1', 'variant_expt_relational_2',
# 'variant_missilecommand_1','variant_missilecommand_2', 'variant_missilecommand_3', 'variant_missilecommand_4', 'variant_survivezombies_1', 'variant_survivezombies_2',
# # ### 5x
# # 'aliens','avoidgeorge','bait','bees_and_birds','boulderdash','closing_gates','corridor','expt_antagonist','expt_ee','expt_helper',
# #  'expt_preconditions','expt_push_boulders','expt_relational','frogs','jaws','lemmings','myAliens','plaqueattack','portals','sokoban','surprise','survivezombies',
# #  'variant_aliens_1','variant_aliens_2','variant_aliens_3','variant_aliens_4','variant_avoidgeorge_1','variant_avoidgeorge_2','variant_avoidgeorge_3','variant_avoidgeorge_4',
# #  'variant_bait_1','variant_bait_2','variant_boulderdash_1','variant_boulderdash_2','variant_butterflies_1','variant_chase_2','variant_chase_3','variant_corridor_1',
# #  'variant_expt_ee_1','variant_expt_ee_3','variant_expt_helper_1','variant_expt_helper_2','variant_frogs_1','variant_frogs_2','variant_frogs_3','variant_jaws_1',
# #  'variant_jaws_2','variant_lemmings_1','variant_lemmings_2','variant_lemmings_3','variant_myAliens_1','variant_myAliens_2','variant_plaqueattack_1',
# #  'variant_plaqueattack_2','variant_plaqueattack_3','variant_portals_1','variant_portals_2','variant_sokoban_1','variant_sokoban_2','variant_surprise_1',
# #  'variant_surprise_2','variant_watergame_1','variant_watergame_2','variant_zelda_1','variant_zelda_2','variant_zelda_3','watergame','zelda'
# ]


##### no gradient
## 10x
# game_names = ['variant_aliens_1', 'variant_aliens_2', 'variant_aliens_3', 'variant_aliens_4', 
# 'avoidgeorge', 'variant_avoidgeorge_1', 'variant_avoidgeorge_2', 'variant_avoidgeorge_3', 'variant_avoidgeorge_4',
# 'bait', 'variant_bait_1', 'variant_bait_2',
# 'bees_and_birds','variant_bees_and_birds_1',  
# 'butterflies', 'variant_butterflies_1', 'variant_butterflies_2', 
# 'boulderdash', 'variant_boulderdash_1', 'variant_boulderdash_2',
# 'chase', 'variant_chase_1', 'variant_chase_2', 'variant_chase_3', 
# 'closing_gates', 'variant_closing_gates_1',
# 'corridor','variant_corridor_1', 
# 'expt_antagonist', 'variant_expt_antagonist_1','variant_expt_antagonist_2', 
# 'expt_ee', 'variant_expt_ee_1', 'variant_expt_ee_2', 'variant_expt_ee_3', 
# 'expt_helper', 'variant_expt_helper_1', 'variant_expt_helper_2', 
# 'expt_preconditions', 'variant_expt_preconditions_1', 'variant_expt_preconditions_2',
# 'expt_push_boulders', 'variant_expt_push_boulders_1', 'variant_expt_push_boulders_2', 
# 'expt_relational', 'variant_expt_relational_1', 'variant_expt_relational_2',
# 'frogs', 'variant_frogs_1', 'variant_frogs_2', 'variant_frogs_3',
# 'jaws', 'variant_jaws_1', 'variant_jaws_2',
# 'lemmings', 'variant_lemmings_1',  'variant_lemmings_2', 'variant_lemmings_3',
# 'missilecommand', 'variant_missilecommand_1', 'variant_missilecommand_2', 'variant_missilecommand_3', 'variant_missilecommand_4',
# 'myAliens', 'variant_myAliens_1', 'variant_myAliens_2',
# 'plaqueattack', 'variant_plaqueattack_1', 'variant_plaqueattack_2', 'variant_plaqueattack_3',
# 'portals', 'variant_portals_1', 'variant_portals_2',
# 'surprise', 'variant_surprise_1', 'variant_surprise_2',
# 'survivezombies', 'variant_survivezombies_1', 'variant_survivezombies_2',
# 'sokoban', 'variant_sokoban_1', 'variant_sokoban_2',
# 'watergame', 'variant_watergame_1', 'variant_watergame_2',
# 'zelda','variant_zelda_1', 'variant_zelda_2', 'variant_zelda_3',

# #5x
# 'aliens'
# ] #90 total

# #### no subgoals ### need to rerun some of this after checking what got through before the /om2 interruption.
## 10x
# game_names = ['variant_aliens_1', 'variant_aliens_2', 'variant_aliens_3', 'variant_aliens_4', 
# 'avoidgeorge', 'variant_avoidgeorge_1', 'variant_avoidgeorge_2', 'variant_avoidgeorge_3', 'variant_avoidgeorge_4',
# 'bait', 'variant_bait_1', 'variant_bait_2',
# 'bees_and_birds','variant_bees_and_birds_1',  
# 'butterflies', 'variant_butterflies_1', 'variant_butterflies_2', 
# 'boulderdash', 'variant_boulderdash_1', 'variant_boulderdash_2',
# 'chase', 'variant_chase_1', 'variant_chase_2', 'variant_chase_3', 
# 'closing_gates', 'variant_closing_gates_1',
# 'corridor','variant_corridor_1', 
# 'expt_antagonist', 'variant_expt_antagonist_1','variant_expt_antagonist_2', 
# 'expt_ee', 'variant_expt_ee_1', 'variant_expt_ee_2', 'variant_expt_ee_3', 
# 'expt_helper', 'variant_expt_helper_1', 'variant_expt_helper_2', 
# 'expt_preconditions', 'variant_expt_preconditions_1', 'variant_expt_preconditions_2',
# 'expt_push_boulders', 'variant_expt_push_boulders_1', 'variant_expt_push_boulders_2', 
# 'expt_relational', 'variant_expt_relational_1', 'variant_expt_relational_2',
# 'frogs', 'variant_frogs_1', 'variant_frogs_2', 'variant_frogs_3',
# 'jaws', 'variant_jaws_1', 'variant_jaws_2',
# 'lemmings', 'variant_lemmings_1',  'variant_lemmings_2', 'variant_lemmings_3',
# 'missilecommand', 'variant_missilecommand_1', 'variant_missilecommand_2', 'variant_missilecommand_3', 'variant_missilecommand_4',
# 'myAliens', 'variant_myAliens_1', 'variant_myAliens_2',
# 'plaqueattack', 'variant_plaqueattack_1', 'variant_plaqueattack_2', 'variant_plaqueattack_3',
# 'portals', 'variant_portals_1', 'variant_portals_2',
# 'surprise', 'variant_surprise_1', 'variant_surprise_2',
# 'survivezombies', 'variant_survivezombies_1', 'variant_survivezombies_2',
# 'sokoban', 'variant_sokoban_1', 'variant_sokoban_2',
# 'watergame', 'variant_watergame_1', 'variant_watergame_2',
# 'zelda','variant_zelda_1', 'variant_zelda_2', 'variant_zelda_3',

# #5x
# 'aliens'
# ] #90 total

# ## no subgoals + no gradient
# ## 10x
# game_names = ['variant_expt_preconditions_1', 'variant_expt_preconditions_2', 'variant_expt_push_boulders_1', 'variant_expt_push_boulders_2',

# # ## 5x
# 'aliens', 'variant_aliens_1', 'variant_aliens_2', 'variant_aliens_3', 'variant_aliens_4', 
# 'avoidgeorge', 'variant_avoidgeorge_1', 'variant_avoidgeorge_2', 'variant_avoidgeorge_3', 'variant_avoidgeorge_4',
# 'bait', 'variant_bait_1', 'variant_bait_2',
# 'bees_and_birds','variant_bees_and_birds_1',  
# 'butterflies', 'variant_butterflies_1', 'variant_butterflies_2', 
# 'boulderdash', 'variant_boulderdash_1', 'variant_boulderdash_2',
# 'chase', 'variant_chase_1', 'variant_chase_2', 'variant_chase_3', 
# 'closing_gates', 'variant_closing_gates_1',
# 'corridor','variant_corridor_1', 
# 'expt_antagonist', 'variant_expt_antagonist_1','variant_expt_antagonist_2', 
# 'expt_ee', 'variant_expt_ee_1', 'variant_expt_ee_2', 'variant_expt_ee_3', 
# 'expt_helper', 'variant_expt_helper_1', 'variant_expt_helper_2', 
# 'expt_preconditions',
# 'expt_push_boulders',
# 'expt_relational', 'variant_expt_relational_1', 'variant_expt_relational_2',
# 'frogs', 'variant_frogs_1', 'variant_frogs_2', 'variant_frogs_3',
# 'jaws', 'variant_jaws_1', 'variant_jaws_2',
# 'lemmings', 'variant_lemmings_1',  'variant_lemmings_2', 'variant_lemmings_3',
# 'missilecommand', 'variant_missilecommand_1', 'variant_missilecommand_2', 'variant_missilecommand_3', 'variant_missilecommand_4',
# 'myAliens', 'variant_myAliens_1', 'variant_myAliens_2',
# 'plaqueattack', 'variant_plaqueattack_1', 'variant_plaqueattack_2', 'variant_plaqueattack_3',
# 'portals', 'variant_portals_1', 'variant_portals_2',
# 'surprise', 'variant_surprise_1', 'variant_surprise_2',
# 'survivezombies', 'variant_survivezombies_1', 'variant_survivezombies_2',
# 'sokoban', 'variant_sokoban_1', 'variant_sokoban_2',
# 'watergame', 'variant_watergame_1', 'variant_watergame_2',
# 'zelda','variant_zelda_1', 'variant_zelda_2', 'variant_zelda_3']


# ## no IW
# ##10x
game_names = ['expt_helper', 'variant_aliens_2', 'variant_aliens_3', 'variant_jaws_2', 'variant_myAliens_1', 'variant_sokoban_2',
'variant_expt_relational_1', 'variant_surprise_2',
'variant_expt_preconditions_1', 'variant_expt_preconditions_2', 'variant_expt_push_boulders_1', 'variant_expt_push_boulders_2',

## 5x
'aliens', 'variant_aliens_1', 'variant_aliens_4', 
'avoidgeorge', 'variant_avoidgeorge_1', 'variant_avoidgeorge_2', 'variant_avoidgeorge_3', 'variant_avoidgeorge_4',
'bait', 'variant_bait_1', 'variant_bait_2',
'bees_and_birds','variant_bees_and_birds_1',  
'butterflies', 'variant_butterflies_1', 'variant_butterflies_2', 
'boulderdash', 'variant_boulderdash_1', 'variant_boulderdash_2',
'chase', 'variant_chase_1', 'variant_chase_2', 'variant_chase_3', 
'closing_gates', 'variant_closing_gates_1',
'corridor','variant_corridor_1', 
'expt_antagonist', 'variant_expt_antagonist_1','variant_expt_antagonist_2', 
'expt_ee', 'variant_expt_ee_1', 'variant_expt_ee_2', 'variant_expt_ee_3', 
'variant_expt_helper_1', 'variant_expt_helper_2', 
'expt_preconditions', 
'expt_push_boulders',
'expt_relational', 'variant_expt_relational_2',
'frogs', 'variant_frogs_1', 'variant_frogs_2', 'variant_frogs_3',
'jaws', 'variant_jaws_1',
'lemmings', 'variant_lemmings_1',  'variant_lemmings_2', 'variant_lemmings_3',
'missilecommand', 'variant_missilecommand_1', 'variant_missilecommand_2', 'variant_missilecommand_3', 'variant_missilecommand_4',
'myAliens', 'variant_myAliens_2',
'plaqueattack', 'variant_plaqueattack_1', 'variant_plaqueattack_2', 'variant_plaqueattack_3',
'portals', 'variant_portals_1', 'variant_portals_2',
'surprise', 'variant_surprise_1',
'survivezombies', 'variant_survivezombies_1', 'variant_survivezombies_2',
'sokoban', 'variant_sokoban_1',
'watergame', 'variant_watergame_1', 'variant_watergame_2',
'zelda','variant_zelda_1', 'variant_zelda_2', 'variant_zelda_3'] #90 total





