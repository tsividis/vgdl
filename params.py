hyperparameter_sets = [
    {
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': .1,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     },
    {
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': 10.,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     }
]
games_to_hyperparameters = {
	'game1' : [hyperparameter_sets[0], hyperparameter_sets[1], hyperparameter_sets[2]],
	'game2' : [hyperparameter_sets[1]],
	'game3' : [hyperparameter_sets[0]]
}
