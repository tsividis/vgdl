game_string = '''
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		wall > Immovable color=DARKGRAY
		log > Missile speed=1 color=BROWN
	LevelMapping
		A > avatar
		w > wall
		L > log
	TerminationSet
		Termination
'''
level_strings0 = ('''
wwwwwwwwwwwwwww
w             w
w      A      w
wwwwwwwwwwwwwww
''', '''
wwwwwwwwwwwwwww
w             w
w      A      w
wwwwwwwwwwwwwww
''')

level_strings1 = ('''
wwwwwwwwwwwwwww
w             w
w     A       w
wwwwwwwwwwwwwww
''', '''
wwwwwwwwwwwwwww
w             w
w      A      w
wwwwwwwwwwwwwww
''')

level_strings2 = ('''
wwwwwwwwwwwwwww
wA            w
w      LLL    w
wwwwwwwwwwwwwww
''', '''
wwwwwwwwwwwwwww
wA            w
w     LLL     w
wwwwwwwwwwwwwww
''')

level_strings3 = ('''
wwwwwwwwwwwwwww
w             w
w     LLL     w
w     LLL     w
w     LLL     w
w             w
w     A       w
wwwwwwwwwwwwwww
''', '''
wwwwwwwwwwwwwww
w     LLL     w
w     LLL     w
w     LLL     w
w             w
w             w
w     A       w
wwwwwwwwwwwwwww
''')

level_strings4 = ('''
wwwwwwwwwwwwwww
w             w
w      LLL    w
w     LLL     w
w             w
w             w
w     A       w
wwwwwwwwwwwwwww
''', '''
wwwwwwwwwwwwwww
w             w
w     LLL     w
w     LLL     w
w             w
w             w
w     A       w
wwwwwwwwwwwwwww
''')

level_strings5 = ('''
wwwwwwwwwwwwwww
w             w
w    LLL      w
w     LLL     w
w             w
w             w
w     A       w
wwwwwwwwwwwwwww
''', '''
wwwwwwwwwwwwwww
w             w
w     LLL     w
w     LLL     w
w             w
w             w
w     A       w
wwwwwwwwwwwwwww
''')

level_strings6 = ('''
wwwwwwwwwwwwwww
w             w
w     LLL     w
w     LLL     w
w             w
w             w
w     A       w
wwwwwwwwwwwwwww
''', '''
wwwwwwwwwwwwwww
w             w
w      LLL    w
w     LLL     w
w             w
w             w
w     A       w
wwwwwwwwwwwwwww
''')