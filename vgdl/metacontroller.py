import random
from IPython import embed
from hyperparameters import metacontroller_sets
import WBP

class Metacontroller:
    def __init__(self, agent):
        self.agent = agent
        self.display_text = self.agent.display_text
        self.prev_long_term_nodes = metacontroller_sets[0]['longHorizonNodes']
        self.quitting = False

    def isReplanningNecessary(self):
        
        re_plan = False
        ## Make sure agent is far enough from unpredictable dangerous objects.
        # Check for disparities between plan and reality
        # (e.g. stochastic effects)
        if self.agent.steps_in_solution%self.agent.regrounding==0 and self.agent.environment.getTime()>0:
            if (not self.agent.takingRandomSteps) and self.agent.checkForDangerOrAvatarMisLocation(self.agent.environment, self.agent.hypotheses[0], self.agent.predicted_states, self.agent.steps_in_solution):
                re_plan = True
                print "regrounding"

        if self.agent.steps_in_solution >= len(self.agent.solution):
            if self.agent.environment.getTime()==0:
                print "New episode; need to plan."
            else:
                print "No steps remaining in previously-conceived plan; need to re-plan"
            re_plan = True

        ended, win = self.agent.environment._isDone()

        if ended:
            re_plan = False

        return re_plan

    def checkForRepeatedDeaths(self, episodeRecord, cutoff):
        ## Has agent died the same way (i.e., killed by the same object) multiple times? (Used for metacontroller policy)
        count = 1
        for i in range(1, len(episodeRecord)):
            if episodeRecord[i][0]==False and episodeRecord[i][1]==episodeRecord[i-1][1]:
                count+=1
            else:
                break
        if count>cutoff:
            return True
        else:
            return False

    def checkForMovingTypes(self, environment, hypothesis):
        ## Another check for whether agent is in slow-moving games (where it's the only entity that generates motion)
        if hypothesis.classes['avatar'][0].args and 'stype' in hypothesis.classes['avatar'][0].args:
            thingWeShoot = hypothesis.classes['avatar'][0].args['stype']
        else:
            thingWeShoot = None    
        moving_types = [k for k in hypothesis.classes.keys() if k!=thingWeShoot and any([t in str(hypothesis.classes[k][0].vgdlType) for t in ['Missile', 'Random', 'Chaser']])]
        moving_colors = [hypothesis.classes[k][0].color for k in moving_types]
        movingTypes = False
        if moving_colors:
            for s in environment.getAliveSprites():
                if s.colorName in moving_colors:
                    movingTypes = True
                    break
        return movingTypes

    def noNewObjectsInAWhile(self, environment, hypothesis, age_cutoff):
        ## Avoids switching to long-range planning in games where, e.g., things spawn from time to time. For games like that it makes more sense to wait for spawns to happen, rather than assuming you're in a static environment.
        if hypothesis.classes['avatar'][0].args and 'stype' in hypothesis.classes['avatar'][0].args:
            thingWeShoot = hypothesis.classes['avatar'][0].args['stype']
        else:
            thingWeShoot = None         
        
        min_age = min([sprite.lastmove for sprite in environment.getAliveSprites() if sprite.name not in [thingWeShoot, 'avatar']])

        try:
            time_since_last_kill = environment.getTime() - max([item.deathage for item in environment.getDeadSprites() if item.name!=thingWeShoot])
        except:
            time_since_last_kill = environment.getTime()

        if (min_age > age_cutoff) and (time_since_last_kill > age_cutoff):
            return True
        else:
            return False

    def testSwitchHyperparams(self, new_hyperparameter):
        self.agent.hyperparameter_index = new_hyperparameter

    def setMaxNodes(self):
        ## You don't anneal max_nodes up for shortHorizon planning. Randomly pick a horizon from [200,500,1000] each time. (Did this to save on compute -- doing 1k each time would be strictly better).
        if self.agent.shortHorizon and self.agent.shortHorizonRandomChoice:
            self.agent.max_nodes = random.choice(self.agent.shortHorizonRandomChoice)
        else:
            self.agent.max_nodes = self.agent.stored_max_nodes

        if self.agent.produce_printout:
            print "==============================================================="
            print "Will plan with max_nodes: {}, short_horizon: {}".format(self.agent.max_nodes, self.agent.shortHorizon)

    def annealUp(self):
        ## Agent failed the game either because it made a mistake it couldn't recover from or because search timed out.
        ## Search more deeply next time.
        forfeit_level = False
        curr_max_nodes = self.agent.max_nodes
        self.agent.max_nodes *= self.agent.max_nodes_annealing
        self.agent.stored_max_nodes = self.agent.max_nodes
        if self.agent.produce_printout:
            print "annealing up from {} to {} nodes".format(curr_max_nodes, self.agent.max_nodes)
        if self.agent.max_nodes > self.agent.absolute_max_nodes:
            if self.agent.produce_printout:
                print "Exceeded absolute_max_nodes of {}. Annealing back down to {} and quitting the level".format(self.agent.absolute_max_nodes, self.agent.max_nodes/self.agent.max_nodes_annealing)
            self.agent.max_nodes /= self.agent.max_nodes_annealing
            self.agent.stored_max_nodes = self.agent.max_nodes
            self.agent.forfeit_level = True
        return forfeit_level

    ##overload the agent functions so that you can call them directly from here

    def determinePlanningModeAndReplanIfNecessary(self, solution, env, planner_recommended_quitting):
        self.display_text = True
        self.agent.produce_printout = True
        predicted_states, printable_predicted_states = self.agent.predicted_states, self.agent.printable_predicted_states

        if not solution:
            print("HULLO")
            # ## If planner didn't give a solution, switch modes according to metacontroller policy
            # if self.checkForRepeatedDeaths(self.agent.episodeRecord, 2):
            #     if self.agent.hyperparameter_index == 'long-term':
            #         new_index = 'long-term' ## don't switch away from idx_1
            #         stall_mode = False
            #     if self.agent.hyperparameter_index == 'short-term':
            #         if self.display_text:
            #             print "Repeated deaths. Switching to long-range planning"
            #         new_index = 'long-term'
            #         stall_mode = False
            #     planner_hyperparameters = self.agent.hyperparameterSwitch(new_index=new_index)

            # elif self.agent.hyperparameter_index == 'short-term':
                
            #     ## Do things move?
            #     movingTypes = self.checkForMovingTypes(env, self.agent.hypotheses[0])

            #     ## Does the score change with each time-step?
            #     if len(self.agent.bookkeeping.compactStates)>1 and env.getTime()>self.agent.bookkeeping.compactStates[-2]['timestep']:
            #         scoreChange = env.getScore()!=self.agent.bookkeeping.compactStates[-2]['score']
            #     else:
            #         scoreChange = False

            #     if self.display_text:
            #         print "moving types: {}".format(movingTypes)
            #         print "noNewObjectsInAWhile: {}".format(self.noNewObjectsInAWhile(env, self.agent.hypotheses[0], self.agent.noNewObjectNum))
            #         print "scoreChange: {}".format(scoreChange)
            #     if self.noNewObjectsInAWhile(env, self.agent.hypotheses[0], self.agent.noNewObjectNum) and \
            #             (not movingTypes or (movingTypes and not scoreChange)):
            #         if self.agent.produce_printout:
            #             print "switching to long-range planning"
            #         ## switch to long-range planning
            #         new_index = 'long-term'
            #         planner_hyperparameters = self.agent.hyperparameterSwitch(new_index=new_index)
            #         stall_mode = False
            #     else:
            #         if self.agent.produce_printout:
            #             print "planning in 'stall' mode"
            #         new_index = 'short-term'
            #         planner_hyperparameters = self.agent.hyperparameterSwitch(new_index=new_index)
            #         stall_mode = True
            #         self.agent.stored_max_nodes = self.agent.max_nodes ##taking annealing into account
            #         self.agent.max_nodes = self.agent.stall_mode_max_nodes
            # else:
            #     stall_mode = False

            # # if self.display_text:
            # print "planning in {} mode".format(self.agent.hyperparameter_index)
            # print "max_nodes: {}, short_horizon: {}, stall_mode: {}".format(self.agent.max_nodes, self.agent.shortHorizon, stall_mode)

            # if stall_mode: #aka 'stall' mode
            #     ## Replan in new mode
            #     p = WBP.WBP(self.agent.theoryRLEs[0], self.agent.gameFilename, theory=self.agent.hypotheses[0], fakeInteractionRules = self.agent.fakeInteractionRules,
            #         seen_limits = self.agent.seen_limits, max_nodes=self.agent.max_nodes, return_subgoal_plans=self.agent.return_subgoal_plans, stall_mode=stall_mode, hyperparameters=planner_hyperparameters, 
            #         extra_atom=self.agent.extra_atom, IW_k=self.agent.IW_k, lesion=self.agent.planner_lesion)
            #     planner_recommended_quitting = p.quitting
            #     p.BFS()
            #     self.agent.total_planner_steps += p.total_nodes_opened
            #     self.agent.planner_nodes_opened_on_most_recent_step = p.total_nodes_opened

            #     solution = p.solution
            #     predicted_states = p.predicted_states
            #     printable_predicted_states = p.printable_predicted_states


            # select random planning mode
            planning_mode = random.choice(['long-term', 'short-term', 'stall-mode'])

            print("Planning in {}".format(planning_mode))
            
            if planning_mode in ['long-term', 'short-term']:
                planner_hyperparameters = self.agent.hyperparameterSwitch(new_index=planning_mode)
                if planning_mode == 'long-term':
                    self.agent.max_nodes = self.prev_long_term_nodes
                    self.agent.stored_max_nodes = self.agent.max_nodes
            else:
                stall_mode = True
                planner_hyperparameters = self.agent.hyperparameterSwitch(new_index='short-term')
                self.agent.stored_max_nodes = self.agent.max_nodes
                self.agent.max_nodes = self.agent.stall_mode_max_nodes

                # get solution and predicted states
                p = WBP.WBP(self.agent.theoryRLEs[0], self.agent.gameFilename, theory=self.agent.hypotheses[0], fakeInteractionRules = self.agent.fakeInteractionRules,
                    seen_limits = self.agent.seen_limits, max_nodes=self.agent.max_nodes, return_subgoal_plans=self.agent.return_subgoal_plans, stall_mode=stall_mode, hyperparameters=planner_hyperparameters, 
                    extra_atom=self.agent.extra_atom, IW_k=self.agent.IW_k, lesion=self.agent.planner_lesion)
                planner_recommended_quitting = p.quitting
                p.BFS()
                self.agent.total_planner_steps += p.total_nodes_opened
                self.agent.planner_nodes_opened_on_most_recent_step = p.total_nodes_opened

                solution = p.solution
                predicted_states = p.predicted_states
                printable_predicted_states = p.printable_predicted_states    

        self.agent.takingRandomSteps = False

        if (not solution) or planner_recommended_quitting:

            self.agent.steps_in_solution = 0

            # Here we make a distinction between quitting because you've
            # exhausted the number of nodes you can visit or because you
            # ran out of novelty. In the first case, you only wait longer,
            # in the second case, you also add a new atom to IW
            if self.agent.extra_atom_allowed:
                if self.display_text:
                    print "turning on extra atom"
                self.agent.extra_atom = True
            
            ## if you don't get a plan with short-horizon mode you'll plan in stall mode. You only get here if you're in long-term planning and don't find a plan.
            if self.agent.longHorizonObservations<self.agent.longHorizonObservationLimit: 
                if self.agent.produce_printout:
                    print "Didn't get solution. Taking {} random steps and then replanning".format(self.agent.random_steps_on_plan_failure)
                solution = [] ## You may have gotten p.quitting but also a solution; make sure you don't try to act on that if the planner decided it wasn't worth it.
                for i in range(self.agent.random_steps_on_plan_failure):
                    solution.append(random.choice(self.agent.hypotheses[0].getLegalActions()))
                self.agent.longHorizonObservations += 1
                self.agent.takingRandomSteps = True
            else:
                self.annealUp()
                # set prev nodes to continue annealing
                self.prev_long_term_nodes = self.agent.max_nodes
                self.quitting = True
                print "DECIDING TO QUIT"

        else:
            print "No need to switch hyperparameters. Staying in {} mode".format(self.agent.hyperparameter_index)

        return solution, predicted_states, printable_predicted_states