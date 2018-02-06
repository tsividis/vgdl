import argparse
import vgdl.agent as agent

parser = argparse.ArgumentParser(description='Run the RLE.')
parser.add_argument('-g', '--game', 
						help='Game name in examples. Defaults to gridphysics.avatar_inference',
						default='gridphysics.avatar_inference')

# Playing GVG-AI games
def read_gvgai_game(game_name):
	with open(game_name, 'r') as f:
		new_doc = []
		g = gen_color()
		for line in f.readlines():
			new_line = (" ".join([string if string[:4]!="img="
				else "color={}".format(next(g))
				for string in line.split(" ")]))
			new_doc.append(new_line)
		new_doc = "\n".join(new_doc)
	return new_doc

def gen_color():
	from vgdl.colors import colorDict
	color_list = colorDict.values()
	color_list = [c for c in color_list if c not in ['UUWSWF']]
	for color in color_list:
		yield color

if __name__ == '__main__':
	args = parser.parse_args()
	
	game_name = 'examples.' + args.game

	# Important for running agent (probably).
	global WBP
	if 'grid' in game_name:
		import vgdl.WBP_grid as WBP
	else:
		import vgdl.WBP_continuous as WBP

	level_game_pairs = None

	a = agent.Agent('full', game_name)

	a.testCurriculum(level_game_pairs=None)


