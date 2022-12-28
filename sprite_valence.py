# For each game, whether each sprite is approach/avoid/neutral

valences = set(['approach','avoid','neutral'])

sprite_valences = {
        "vgfmri3_chase": {
            "approach_colors": ["RED"],
            "avoid_colors": ["GOLD"],
            "approach": ["scared"],
            "avoid": ["angry"],
            "neutral": ["carcass", "wall"]
        },
        "vgfmri3_helper": {
            "approach_colors": ["WHITE", "YELLOW", "GREEN"],
            "avoid_colors": [],
            "approach": ["box1","box2","box3"],
            "avoid": [],
            "neutral": ["forcefield","wall","chaser1","chaser2"]
        },
        "vgfmri3_bait": {
            "approach_colors": ["RED", "ORANGE", "GREEN", "BROWN", "RESOURCETOADD"],
            "avoid_colors": ["BLUE"],
            "approach": ["mushroom","key","goal","box"],
            "avoid": ["hole"],
            "neutral": ["wall"]
        },
        "vgfmri3_lemmings": {
            "approach_colors": ["GREEN", "RED"],
            "avoid_colors": ["LIGHTBLUE"],
            "approach": ["goal","lemming"],
            "avoid": ["hole"],
            "neutral": ["shovel","entrance","wall"]
        },
        "vgfmri3_plaqueAttack": {
            "approach_colors": ["ORANGE", "BROWN", "GREEN", "BLUE"],
            "avoid_colors": [],
            "approach": ["deadMolarInf","deadMolarSup","hotdog","burger"],
            "avoid": [],
            "neutral": ["fullMolarInf","fullMolarSup","hotdoghole","burgerhole","fluor","wall"]
        },
        "vgfmri3_zelda": {
            "approach_colors": ["ORANGE", "GREEN", "RESOURCETOADD"],
            "avoid_colors": ["GOLD", "BROWN", "PINK"],
            "approach": ["key","goal"],
            "avoid": ["monsterQuick","monsterNormal","monsterSlow"],
            "neutral": ["wall","sword"]
        },

        "vgfmri4_chase": {
            "approach_colors": ["RED"],
            "avoid_colors": ["GOLD"],
            "approach": ["scared"],
            "avoid": ["angry"],
            "neutral": ["carcass", "wall"]
        },
        "vgfmri4_helper": {
            "approach_colors": ["WHITE", "YELLOW", "GREEN"],
            "avoid_colors": [],
            "approach": ["box1","box2","box3"],
            "avoid": [],
            "neutral": ["forcefield","wall","chaser1","chaser2"]
        },
        "vgfmri4_bait": {
            "approach_colors": ["PURPLE", "ORANGE", "BROWN", "BLACK", "RESOURCETOADD"],
            "avoid_colors": ["YELLOW"],
            "approach": ["mushroom","key","goal","box"],
            "avoid": ["hole"],
            "neutral": ["wall"]
        },
        "vgfmri4_lemmings": {
            "approach_colors": ["GREEN", "RED"],
            "avoid_colors": ["LIGHTBLUE"],
            "approach": ["goal","lemming"],
            "avoid": ["hole"],
            "neutral": ["shovel","entrance","wall"]
        },
        "vgfmri4_avoidgeorge": {
            "approach_colors": ["PURPLE"],
            "avoid_colors": ["YELLOW"],
            "approach": ["annoyed"],
            "avoid": ["george"],
            "neutral": ["wall","cigarette","quiet"]
        },
        "vgfmri4_zelda": {
            "approach_colors": ["ORANGE", "GREEN", "RESOURCETOADD"],
            "avoid_colors": ["GOLD", "BROWN", "PINK"],
            "approach": ["key","goal"],
            "avoid": ["monsterQuick","monsterNormal","monsterSlow"],
            "neutral": ["wall","sword"]
        },
}
