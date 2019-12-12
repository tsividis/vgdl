from ontology import *

# ---------------------------------------------------------------------
#     Dyanmic-type inference
#     'Sprites' refer to dynamic types
# ---------------------------------------------------------------------

# Types in our hypothesis space
sprite_types = [ResourcePack, RandomNPC, Missile, Chaser]

# Fields over which we do inference for each dynamic type
spriteToParams = {'Resource': [], \
                'ResourcePack': [], \
                'RandomNPC': ['cooldown', 'speed'], \
                'Chaser': ['cooldown', 'fleeing', 'stype', 'speed'], \
                'AStarChaser': ['fleeing', 'speed', 'stype'], \
                'OrientedSprite': ['orientation'], \
                'Missile': ['speed', 'orientation', 'cooldown']}

class dynamicTypeDistribution():
    def __init__(self):
        self.distribution = {}
        self.movement_options = {} ## rename

    def initializeDistribution(self, sprite_types, objectColors, dynamic_type_lesion=[]):
        """
        Creates a uniform distribution over all parameter combinations
        """
        catch_all_prior = .000001
        outList = []
        if 'Chaser' in dynamic_type_lesion:
            try:
                sprite_types.remove(Chaser)
            except:
                pass
        if 'Missile' in dynamic_type_lesion:
            try:
                sprite_types.remove(Missile)
            except:
                pass
        for sprite_type in sprite_types:
                paramList = self.initializeDistributionArgs(sprite_type, objectColors, dynamic_type_lesion)
                for element in itertools.product(*paramList):
                    outList.append(tuple([('vgdlType', sprite_type)]+sorted(element)))
        initial_distribution = {k:1.0 for k in outList}
        initial_distribution[(('vgdlType', 'OTHER'), )] = catch_all_prior
        return initial_distribution


    def initializeDistributionArgs(self, sprite_type, objectColors, dynamic_type_lesion=[]):
        """
        Given a sprite type, this returns a distribution over the kinds of args (parameters) belonging
        to that sprite type.
        This is where the hypothesis space for each individual sprite type is outlined. Could expand this at the cost of more compute
        """

        def initializeSpeed():
            if 'speed' in dynamic_type_lesion:
                speedValues = [0.2, 0.4, 0.6, 0.8, 1.]
            else:
                speedValues = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]
            return [('speed', v) for v in speedValues]

        def initializeOrientation():
            orientationValues = [LEFT, RIGHT, UP, DOWN]
            return [('orientation', v) for v in orientationValues]

        def initializeFleeing():
            fleeingValues = [True, False]
            return [('fleeing', v) for v in fleeingValues]

        def initializeStype():
            stypeValues = [o for o in objectColors if o not in ['BLACK', 'DARKGRAY', 'MPUYEI', 'NUPHKK', 'SCJPNE']]
            return [('stype', v) for v in stypeValues]

        def initializeCooldown():
            stypeValues = [1, 2, 3, 4, 5, 6, 10]
            return [('cooldown', v) for v in stypeValues]

        paramList = []
        spriteParams = spriteToParams[sprite_type.__name__]

        for s in spriteParams:
            if s == "speed":
                paramList.append(initializeSpeed())
            elif s == "fleeing":
                paramList.append(initializeFleeing())
            elif s == "orientation":
                paramList.append(initializeOrientation())
            elif s=='stype':
                paramList.append(initializeStype())
            elif s=='cooldown':
                paramList.append(initializeCooldown())

        return paramList

    def distributionInitSetup(self, game, sprite, dynamic_type_lesion=[]):
        """
        Does setup for initializing distribution
        'sprite' is an object ID
        """
        objectColors = set()
        for k in game.sprite_constr.keys():
            try:
                if game.sprite_constr[k][1]['color'] not in ['BLACK', 'DARKGRAY', 'MPUYEI', 'NUPHKK', 'SCJPNE']:
                    objectColors.add(colorDict[str(game.sprite_constr[k][1]['color'])])
            except KeyError:
                continue
        objectColors = list(objectColors)
        if 'DTIZDF' in objectColors:
            print "found DTIZDF"
            embed()
        self.distribution[sprite] = self.initializeDistribution(sprite_types, objectColors, dynamic_type_lesion) # Indexed by object ID

        if sprite not in game.all_objects.keys():
            game.all_objects[sprite] = game.getObjects()[sprite]

        self.movement_options[sprite] = {k:{} for k in self.distribution[sprite].keys()}

    def updateDistribution(self, game, sprite, curr_distribution, outcome, specialID=None, missileOrientationClustering=False):

        # For computing the new normalized likelihoods, we proceed as follows:

        # The normalized likelihood for a given observation sequence o_1, ... o_t-1 given a parameter p_j is:
        #   p(o_1, ..., o_t-1|p_j) / sum_i(p(o_1, .., o_t-1|p_i))
        #
        # We want to arrive at the new normalized likelihoods p(o_1, ..., o_t-1, o_t|p_j) / sum_i(p(o_1, .., o_t-1, o_t|p_i))
        #
        # We first compute the ratio between the normalization constants:
        # sum_i(p(o_1, .., o_t-1, o_t|p_i)) / sum_j(p(o_1, .., o_t-1|p_j)) =
        # sum_i(p(o_1, .., o_t-1|p_i) * p(o_t|p_i)) / sum_j(p(o_1, .., o_t-1|p_j))
        #
        # Now, we can get the new normalized likelihood by doing:
        # p(o_1, ..., o_t-1, o_t|p_j) / sum_i(p(o_1, .., o_t-1, o_t|p_i)) =
        #   p(o_1, ..., o_t-1|p_j) / sum_i(p(o_1, .., o_t-1|p_i)) *
        #   p(o_t|p_j)
        #   sum_i(p(o_1, .., o_t-1|p_i) * p(o_t|p_i)) / sum_k(p(o_1, .., o_t-1|p_k))

        epsilon_prob = 0.000005
        normalization_ratio = 0
        alpha = 1.

        movement_options = self.movement_options

        if sprite in curr_distribution.keys():
            for param_combination in curr_distribution[sprite].keys():
                if outcome in movement_options[sprite][param_combination].keys():
                    if missileOrientationClustering and 'Missile' in str(param_combination[0][1]):
                        normalization_ratio += curr_distribution[sprite][param_combination] * (movement_options[sprite][param_combination][outcome]**alpha)
                    else:
                        normalization_ratio += curr_distribution[sprite][param_combination] * movement_options[sprite][param_combination][outcome]
                else:
                    normalization_ratio += curr_distribution[sprite][param_combination] * epsilon_prob

        if sprite in curr_distribution.keys():
            for param_combination in curr_distribution[sprite].keys():
                if outcome in movement_options[sprite][param_combination].keys():
                    if missileOrientationClustering and 'Missile' in str(param_combination[0][1]):
                        curr_distribution[sprite][param_combination] *= ((movement_options[sprite][param_combination][outcome]**alpha) / normalization_ratio)
                    else:
                        curr_distribution[sprite][param_combination] *= (movement_options[sprite][param_combination][outcome] / normalization_ratio)
                else:
                    curr_distribution[sprite][param_combination] *= (epsilon_prob / normalization_ratio)

        return curr_distribution

    def updateOptions(self, game, sprite_type_tuple, current_sprite, params={}, missileOrientationClustering=False):
        """
        Update likelihoods for object passed as 'current_sprite', given the parameter vector in 'sprite_type_tuple'.

        This method gets all of the parameter information from the params variable
        instead of directly accessing the parameters in current_sprite.
        game - current game object
        sprite_type - the sprite type class hypothesis
        current_sprite - the current sprite object
        params - inferred params of the sprite. A dict mapping parameters (as strings) to their values.
        The default value of params is an empty dictionary - if that's the value passed, then the method will
        assume default values for each attribute.
        """
        sprite_type = sprite_type_tuple[1]

        if sprite_type in [Immovable, Passive, ResourcePack, Resource, 'OTHER']:
            return {(current_sprite.rect.left, current_sprite.rect.top): 1.}, {(current_sprite.rect.left, current_sprite.rect.top): 1.} ##object stays in position

        # Chaser
        elif sprite_type == Chaser:
            speed = getSpeed(params)
            fleeing = getFleeing(params)
            targetColor = getStype(params)
            cooldown = getCooldown(params)

            realCooldown = int(current_sprite.cooldown)
            current_sprite.cooldown = cooldown
            
            targets = getTargets(game, targetColor)

            options = []
            position_options = {}

            try:
                for target in targets:
                    options.extend(chaserMovesToward(current_sprite, game, target, fleeing))
                if len(options) == 0:
                    options = BASEDIRS

                for option in options:
                    left, top = current_sprite.physics.calculateActiveMovement(current_sprite, option, speed=speed, is_chaser=True)
                    if (left, top) in position_options.keys():
                        position_options[(left, top)] += 1.0/len(options)
                    else:
                        position_options[(left, top)] = 1.0/len(options)

            except AttributeError: # deals with following error: 'Immovable' object has no attribute 'stype'
                position_options = {(current_sprite.rect.left, current_sprite.rect.top): 1.}

            current_sprite.cooldown = realCooldown
            return position_options, position_options

        # Random NPC
        elif sprite_type == RandomNPC:

            realCooldown = int(current_sprite.cooldown)
            speed, cooldown = getSpeed(params), getCooldown(params)
            current_sprite.cooldown = cooldown
            position_options = {}

            for option in BASEDIRS:
                left, top = current_sprite.physics.calculateActiveMovement(current_sprite, option, speed=speed)
                if (left, top) in position_options.keys():
                    position_options[(left, top)] += 1.0/len(BASEDIRS)
                else:
                    position_options[(left, top)] = 1.0/len(BASEDIRS)

            current_sprite.cooldown = realCooldown
            return position_options, position_options

        # Missile or OrientedSprite
        elif sprite_type in [Missile, OrientedSprite]:

            if not current_sprite.is_static and not current_sprite.only_active:
                # NOTE: we might want to consider having is_static and only_active be
                # parameters that we have to infer, rather than things we get for free.
                # (i.e. make these fields in the params variable)
                speed = getSpeed(params)
                orientation = getOrientation(params)
                cooldown = getCooldown(params)
                realCooldown = int(current_sprite.cooldown)
                current_sprite.cooldown = cooldown
                
                coords = current_sprite.physics.calculatePassiveMovementGivenParams(current_sprite, speed, orientation)
                
                # If object has speed = 0 or no 'orientation' attribute
                position_options, clustered_position_options = {}, {}
                
                if coords == None:
                    return position_options, position_options

                position_options[(coords[0], coords[1])] = 1.

                if missileOrientationClustering:

                    clustered_position_options[(coords[0], coords[1])] = 1.

                    epsilon_prob = 0.005
                    #flip orientation
                    orientation = (orientation[0]*-1, orientation[1]*-1)

                    coords = current_sprite.physics.calculatePassiveMovementGivenParams(current_sprite, speed, orientation)
                    clustered_position_options[(coords[0], coords[1])] = 1.-epsilon_prob                

                current_sprite.cooldown = realCooldown
                return position_options, clustered_position_options

            # Catches objects that can't be Oriented Sprite and Missile types b/c fails the if-statement
            return {}, {}

    def spriteInduction(self, game, memory, step, bestSpriteTypeDict, oldSpriteSet=None, dynamic_type_lesion=[]):
            """
            game = a BasicGame object
            self.distribution is a dictionary of the following form:
            {sprite: {sprite_type: {'prob': PROBABILITY OF SPRITE TYPE, 'args': {'speed': {A VALUE OF SPEED: PROBABILITY OF THAT VALUE}}},
            ...}, ...}
            self.distribution tells you the probability of a sprite being being a particular type. It also
            tells you the probability distribution over values for each parameter (e.g. speed, orientation).
            self.movement_options is a dictionary of the following form:
            {sprite: {sprite_type: {attributeTuple: {sprite position: probability of that sprite position},...},
            ...}, ...}
            self.movement_options tells you the probability of a sprite being in a particular position, given a certain
            setting of its attributes (e.g. specific values for speed, orientation, etc.) and also given sprite type.
            """
            distributionsHaveChanged = False

            if step==1:
                ## Sprite Induction Part 1:
                ## every time you act, make sure there aren't new objects
                ## if there are, update dynamicTypeDistribution etc.
                objects = game.getObjects()
                kill_list_keys = [s.ID for s in game.kill_list]
                spritestoupdate = 0
                for sprite in objects:
                    if objects[sprite]['sprite'].colorName not in ['DARKGRAY', 'MPUYEI', 'NUPHKK', 'SCJPNE'] and sprite not in self.distribution:
                        spritestoupdate+=1
                        game.all_objects[sprite] = objects[sprite]
                        self.distributionInitSetup(game, sprite, dynamic_type_lesion)
            elif step == 2:
                ## See the update options for each sprite type the sprite could be
                objects = game.getObjects()

                game = game
                sprite_count, param_count=0, 0

                for sprite in [s for s in self.distribution.keys() if s in objects.keys()]:                  # Keys are the IDs of the game objects
                    sprite_count +=1
                    sprite_obj = objects[sprite]["sprite"]

                    if sprite_obj.name !='avatar':
                        for param_combination in self.distribution[sprite].keys(): # Check each potential sprite type
                            if self.distribution[sprite][param_combination]> 0:    # Make sure sprite_type is an option for sprite, and sprite is not killed
                                param_count +=1

                                sprite_type = param_combination[0]
                                attributeDict = {k:v for k,v in param_combination[1:]}

                                # Get potential next positions for sprite if it were that sprite type
                                # we are sprite_obj, and we are updating the options for where it could be next contingent on its being 'sprite_type'
                                # given a set of potential attribute values, update the movement options
                                # for this attribute tuple (i.e. candidate set of parameters)

                                ## missileOrientationClustering: considers left/right and up/down to be equivalent options in the likelihood
                                ## so that when objects bounce off walls it doesn't dramatically reduce the probability that they are straight-moving objects

                                _, self.movement_options[sprite][param_combination] = self.updateOptions(game, sprite_type, sprite_obj, params=attributeDict, missileOrientationClustering=True)

                game.targetColorDict = dict()
                game.chaserMovesTowardDict = dict()

            elif step==3:
                ## Update sprite distribution based on observations
                objects = game.getObjects()

                for sprite in [s for s in self.distribution.keys() if s in objects.keys() and s not in [k.ID for k in game.kill_list]]:
                    # Keys are the IDs of the game objects
                    sprite_obj = objects[sprite]["sprite"]


                    if all([sprite not in e for e in game.effectList if e[0]!='nothing']) and sprite not in memory.ignoreList and sprite_obj.name != 'avatar':
                        # only update the distribution in this fashion if there are no events for this
                        # time step involving this sprite.

                        outcome = objects[sprite]["position"]

                        self.distribution = self.updateDistribution(game, sprite, self.distribution, \
                                                  outcome, missileOrientationClustering=True)

                        memory.spriteUpdateDict[sprite] += 1
                
                # if game.time == 1:
                    # embed()
                ## Update the global memory
                for k in self.distribution.keys():
                    if k in game.all_objects:
                        try:
                            color = game.all_objects[k]['type']['color']
                        except KeyError:
                            print("got key error when trying to access sprite color")
                            embed()
                        bestSpriteTypeDict[color][k] = self.distribution[k]

                # t1 = time.time()
                sample, distributionsHaveChanged, _ = self.sampleFromDynamicTypeDistribution(game, memory, game.all_objects, bestSpriteTypeDict, oldSpriteSet = oldSpriteSet)

            ## Reset ignoreList so that next time around you do inference about these objects. We skipped them this particular time-step because they had just appeared so we didn't have likelihoods set up for them.
            # self.distribution = self.distribution
            memory.ignoreList = []
            return distributionsHaveChanged

    def sampleFromDynamicTypeDistribution(self, game, memory, all_objects, bestSpriteTypeDict, oldSpriteSet = None, display=False):

        distributionsHaveChanged = False

        sample = []
        exceptions = []

        spriteUpdateDict = memory.spriteUpdateDict
        curr_distribution = self.distribution
        ## For now let's just assume we know the avatar's type and what it shoots, if anything (but not the properties of that thing)
        non_avatar_keys = []
        for k in all_objects.keys():
            if all_objects[k]['sprite'].name != 'avatar':
                non_avatar_keys.append(k)
            else:
                avatar_type = all_objects[k]['sprite'].__class__
                if avatar_type in [FlakAvatar, AimedFlakAvatar, ShootAvatar, AimedAvatar, AimedFlakAvatar]:
                    try:
                        ## Add avatar, and add the attached arguments, i.e., what the avatar shoots.
                        sample.append(Sprite(vgdlType=all_objects[k]['sprite'].__class__, color=all_objects[k]['type']['color'], args={'stype':all_objects[k]['sprite'].stype}))

                        ## Get the object the Avatar shoots, add that.
                        projectile_name = all_objects[k]['sprite'].stype
                        ao = game.sprite_constr[projectile_name]
                        ao_vgdl_type = ao[0]
                        ao_color = colorDict[str(ao[1]['color'])]
                        ao_args = ao[1]
                        if projectile_name in game.singletons:
                            ao_args.update({'singleton': 'True'})
                        sample.append(Sprite(vgdlType=ao_vgdl_type, color=ao_color, className=all_objects[k]['sprite'].stype, args=ao_args))
                        exceptions.append(ao_color)

                    except AttributeError:
                        print "tried and failed to add a shooting avatar type"
                        # embed()
                        # No args in avatar
                        sample.append(Sprite(vgdlType=MovingAvatar, color=all_objects[k]['type']['color']))
                else:
                    sample.append(Sprite(vgdlType=avatar_type, color=all_objects[k]['type']['color']))

        types = list(set([all_objects[k]['type']['color'] for k in non_avatar_keys]) - set(exceptions))  ## We are treating (for now) the object shot by a ShootAvatar, FlakAvatar, etc. separately and not doing inference about it.    
        best_params = {}

        for obj_type in types:
            
            if obj_type in ['DARKGRAY', 'MPUYEI', 'NUPHKK', 'SCJPNE']:
                s = Sprite(vgdlType=ResourcePack, color=obj_type)
                sample.append(s)
                continue

            ## Integrate evidence across all episodes; pick best hypothesis.

            numDict = defaultdict(lambda:[])
            for k in bestSpriteTypeDict[obj_type].keys():
                numDict[spriteUpdateDict[k]].append(k)

            try:
                param_sum = {k:0. for k in bestSpriteTypeDict[obj_type].values()[0].keys()}
            except IndexError:
                # bestSpriteTypeDict has yet to be populated for this object type
                for k, v in game.getObjects().items():
                    if v['features']['color'] == obj_type:
                        bestSpriteTypeDict[obj_type][k] = self.distribution[k]
                param_sum = {k:1. for k in bestSpriteTypeDict[obj_type].values()[0].keys()}

            param_z = 0

            for num, IDs in numDict.items():
                for param in param_sum.keys():
                    tmp_prod = 1.
                    for ID in IDs:
                        if param in bestSpriteTypeDict[obj_type][ID]:
                            tmp_prod *= bestSpriteTypeDict[obj_type][ID][param]
                        elif 'Chaser' in str(param[0][1]):
                            cooldown = [p[1] for p in param if p[0]=='cooldown']
                            cooldown = cooldown[0] if cooldown else 1
                            speed = [p[1] for p in param if p[0]=='speed']
                            speed = speed[0] if speed else 1
                            randomnpc_param = (
                                ('vgdlType', RandomNPC),
                                ('cooldown', cooldown),
                                ('speed', speed)
                            )
                            tmp_prod *= bestSpriteTypeDict[obj_type][ID][randomnpc_param]
                        else:
                            print "problem in param_product"
                            embed()

                    param_sum[param] += num*tmp_prod
                    param_z += num*tmp_prod
            
            if param_z != 0:
                for param,val in param_sum.items():
                    param_sum[param] /= param_z

            best_param = max(param_sum, key=param_sum.get)

            sprite_type = best_param[0][1]

            color = obj_type

            if sprite_type=='OTHER':
                sprite_type = ResourcePack

            s = Sprite(vgdlType=sprite_type, color=color)

            param = dict(best_param[1:])
            setSpriteParams(param, s) # set the parameters for sprite s
            sample.append(s)
            ## Find matching object in the existing hypothesis
            try:
                if oldSpriteSet:
                    if s.color in [sprite.color for sprite in oldSpriteSet]:
                        matchingSprite = [sprite for sprite in oldSpriteSet if s.color==sprite.color][0]
                        # If types are different, distributionsHaveChanged is true
                        if s.vgdlType!=matchingSprite.vgdlType:
                            distributionsHaveChanged = True
                            if display:
                                print ("Distributions for {} have changed from sprite type {} to {}".format(s.color, matchingSprite.vgdlType, s.vgdlType))
                        # If one of the args is None but not the other,
                        # distributionsHaveChanged is true
                        elif ((s.args==None and matchingSprite.args!=None) or
                            (s.args!=None and matchingSprite.args==None)):
                            distributionsHaveChanged = True
                            if display:
                                print ("Distribution args for {} have changed from {} to {}".format(s.color, s.args, matchingSprite.args))
                        elif (s.args and matchingSprite.args) != None:
                            # If args are different, except for the case where only an
                            # orientation is reversed (e.g. turnAround), then
                            # distributionsHaveChanged is true
                            for key in s.args.keys() + matchingSprite.args.keys():
                                try:
                                    if not ((s.args[key] and matchingSprite.args[key])
                                        in ([LEFT, RIGHT] or [UP, DOWN])):
                                        if s.args[key] != matchingSprite.args[key]:
                                            distributionsHaveChanged = True
                                        if display:
                                            print ("Distribution args for {} have changed from {} to {}".format(s.color, s.args, matchingSprite.args))
                                except KeyError:
                                    # If the new sprite has an arg that the old one
                                    # doesn't, or vice-versa, then
                                    # distributionsHaveChanged is true
                                    distributionsHaveChanged = True
                                    if display:
                                        print ("Distribution args for {} have changed from {} to {}".format(s.color, s.args, matchingSprite.args))

                    else:
                        distributionsHaveChanged = True
            except:
                print "failed to find matching object in sampleFromDynamicTypeDistribution"
                embed()
        memory.exceptions = exceptions

        return sample, distributionsHaveChanged, best_params

# ---------------------------------------------------------------------
#     Helper functions
# ---------------------------------------------------------------------

def getSpeed(params):
    """
    params = a dict mapping sprite attributes to values
    sprite = the VGDL sprite.
    """
    if 'speed' in params:
        return params['speed']
    else:
        return 1
        # default speed value

def getFleeing(params):
    """
    params = a dict mapping sprite attributes to values
    sprite = the VGDL sprite.
    """
    if 'fleeing' in params:
        return params['fleeing']
    else:
        return False

def getOrientation(params):
    """
    params = a dict mapping sprite attributes to values
    sprite = the VGDL sprite.
    """
    if 'orientation' in params:
        return params['orientation']

def getStype(params):
    """
    params = a dict mapping sprite attributes to values
    sprite = the VGDL sprite.
    """
    if 'stype' in params:
        return params['stype']

def getCooldown(params):
    if 'cooldown' in params:
        return params['cooldown']
    else:
        return 1

def setSpriteParams(param, sprite):
    """
    param = a dict mapping parameters to values
    sprite = the vgdl sprite
    """
    for p in param:
        if p == "speed":
            sprite.speed = param[p]
        elif p == "fleeing":
            sprite.fleeing = param[p]
        elif p == "orientation":
            sprite.orientation = param[p]
        elif p == "stype":
            sprite.stype = param[p]
        elif p == "cooldown":
            sprite.cooldown = param[p]

def chaserClosestTargets(sprite, game):
    bestd = 1e100
    res = []
    for target in game.getSprites(sprite.stype):
        d = sprite.physics.distance(sprite.rect, target.rect)
        if d < bestd:
            bestd = d
            res = [target]
        elif d == bestd:
            res.append(target)
    return res

def chaserMovesToward(sprite, game, target, fleeing):
    """ Find the canonical direction(s) which move toward
    the target. """
    if (sprite, target, fleeing) in game.chaserMovesTowardDict:
        return game.chaserMovesTowardDict[(sprite, target, fleeing)]

    res = []
    basedist = sprite.physics.distance(sprite.rect, target.rect)

    for a in BASEDIRS:
        r = sprite.rect.copy()
        r = r.move(a)
        newdist = sprite.physics.distance(r, target.rect)

        if fleeing and basedist < newdist:
            res.append(a)
        if not fleeing and basedist > newdist:
            res.append(a)
    game.chaserMovesTowardDict[(sprite, target, fleeing)] = res
    return res

def calculateSpriteMove(game, sprite, speed, orientation):
    if abs(orientation[0])+abs(orientation[1])!=0:
        if speed is None:
            if sprite.speed is None:
                speed = 1
            else:
                speed = sprite.speed
        if speed != 0:# and action is not None:
            speed = float(speed) * game.block_size
        newPos = sprite.rect.left+orientation[0]*speed, sprite.rect.top+orientation[1]*speed
        return (newPos[0], newPos[1])
    return(sprite.rect.left, sprite.rect.top)

def getTargets(game, targetColor):
    t1 = time.time()
    if targetColor not in game.targetColorDict:
        try:
            targetName = [k for k in game.sprite_groups.keys() if game.sprite_groups[k] and game.sprite_groups[k][0].colorName==targetColor][0]
            targets = [s for s in game.sprite_groups[targetName] if s not in game.kill_list]
            # print "target name: {}. target length: {}".format(targetName, len(targets))
        except:
            targets = []
        game.targetColorDict[targetColor] = targets

    return game.targetColorDict[targetColor]

def getKL(dynamicTypeDistribution1, dynamicTypeDistribution2):
    d1, d2 = [v['prob'] for v in dynamicTypeDistribution1.values()], [v['prob'] for v in dynamicTypeDistribution2.values()]
    return scipy.stats.entropy(d1,d2)

def softmax(w, t = 1.0):
    e = np.exp(np.array(w) / t)
    dist = e / np.sum(e)
    return dist