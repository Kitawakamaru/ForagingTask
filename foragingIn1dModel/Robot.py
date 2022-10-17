import pygame
from Agent import Agent
import numpy as np


class RobotLog():
    def __init__(self) -> None:
        '''Creates a structure and support functions to log what the robot does during a simulation
        '''
        self.ticks_in_task_state = [0,0]
        self.ticks_in_social_state = [0,0,0,0]
        self.ticks_in_terrain_state = [0,0]
        self.n_visits_to_food = 0
        self.n_visits_to_home = 0
        self.n_ticks_not_moving = 0
        self.n_passages_through_tunnel_success = 0
        self.n_passages_through_tunnel_fail = 0
        self.n_tunnel_entry = 0
        self.n_tunnel_exit = 0
        self.n_t_visits_home = []



    def printLog(self, cfg):
        print(f'ticks_in_task_state: {self.ticks_in_task_state}')
        print(f'ticks_in_social_state: {self.ticks_in_social_state}')
        print(f'ticks_in_terrain_state: {self.ticks_in_terrain_state}')
        print(f'n_visits_to_food: {self.n_visits_to_food}')
        print(f'n_visits_to_home: {self.n_visits_to_home}')
        print(f'n_ticks_not_moving: {self.n_ticks_not_moving} out of {cfg.TIME_LIMIT/cfg.DT}')
        print(f'n_success_tunnel_passages: {self.n_passages_through_tunnel_success}')
        print(f'n_fail_tunnel_passages: {self.n_passages_through_tunnel_fail}')
        print(f'n_tunnel_entry: {self.n_tunnel_entry}')
        print(f'n_tunnel_exit: {self.n_tunnel_exit}')



    def getLog(self, cfg):
        header = ['ticks_in_task_state', 'ticks_in_social_state', 'ticks_in_terrain_state', 'n_visits_to_food', 
        'n_visits_to_home', 'n_ticks_not_moving', 'n_total_ticks', 'n_success_tunnel_passages', 'n_fail_tunnel_passages',
        'n_tunnel_entry', 'n_tunnel_exit']
        data =  [self.ticks_in_task_state, self.ticks_in_social_state, self.ticks_in_terrain_state, self.n_visits_to_food,
        self.n_visits_to_home, self.n_ticks_not_moving, cfg.TIME_LIMIT/cfg.DT, self.n_passages_through_tunnel_success, 
        self.n_passages_through_tunnel_fail, self.n_tunnel_entry, self.n_tunnel_exit, self.n_t_visits_home]
        return header, data


class Robot(Agent):
    
    def __init__(self, cfg, position: tuple, speed:int):
        '''Creates a simple foraging "ant" which moves in one dimension 
        and attempts to resolve spatial conflicts which occur when it meets another "ant" moving in the opposite direction.
        '''
        super().__init__(position, 1)
        #fixed parameters
        self.aggression_type = cfg.AGGRESSION_TYPES["random"]
        self.speed = speed
        self.fight_range_max = 0
        self.passive_range_max = 0
        self.detection_range_max = 0

        #task parameters
        self.food_position = np.array((5,5))
        self.home_position = np.array((1,1))
        self.tunnel_rect = []

        #variable parameters
        self.fight_range = 0
        self.passive_range = 0
        self.detection_range = 0

        #state at t
        self.task_state = cfg.FORAGING_STATES["going_home"]
        self.target_position = self.food_position
        self.terrain_state = cfg.TERRAIN_STATES["none"]
        self.social_state = cfg.SOCIAL_STATES["navigate"]    
        #self.m_position in super class
        self.state_entry_b = True
        self.time_in_brave = 0
        self.time_in_state = 0
        self.aggression_level = 0
        self.conflict_list = pygame.sprite.Group() 
        self.robots_front = pygame.sprite.Group()
        self.robots_rear = pygame.sprite.Group()
        self.robots = pygame.sprite.Group()
        self.direction = []
        self.has_food_b = False

        self.time_stationary = 0

        #state at t+dt
        self.next_task_state = self.task_state 
        self.next_target_position = self.target_position
        self.next_terrain_state = self.terrain_state
        self.next_social_state = self.social_state
        #self.next_speed = self.speed #speed is the default value which doesn't change!
        self.next_position = self.m_position
        self.next_state_entry_b = self.state_entry_b
        self.next_time_in_brave = self.time_in_brave 
        self.next_aggression_level = self.aggression_level
        self.next_conflict_list = pygame.sprite.Group()
        self.next_direction = []

        #logging
        self.log = RobotLog()
        self.tunnel_state = np.zeros(len(cfg.TUNNEL_STATES))

        #display images.  Expects to find a dictionary containg 3 elements with the keys 'g','y','r'
        self.sprite_images = {}
        self.font_image = []
    #end function



    def initialise(self, cfg, robot_info = {}):
        """Setup for the agent called when the experiment first starts.

        Assume agent_info dict contains:
        {
            home_position: (x,y) [int],
            food_position: (x,y) [int], 
            start_position: (x,y) [int], 
            target_position: (x,y) [int], 
            starting_state: float
            display_scale_factor: float
            fight_threshold_max: float
            passive_threshold_max: float
            detection_threshold_max: float
        }
        """
        self.home_position = robot_info.get("home_position")
        self.food_position = robot_info.get("food_position")

        self.task_state = robot_info.get("starting_state")
        if self.task_state == cfg.FORAGING_STATES["going_home"]:
            self.has_food_b = True
        else:
            #state is finding_food
            self.has_food_b = False
               
        self.target_position = robot_info.get("target_position")
        self.setPosition(robot_info.get("start_position"))
        
        #prints the agents ID number to visualise what's going on and to help when debugging
        if cfg.DRAWSCREEN:
            font = pygame.font.SysFont(None, 48)
            self.font_img = font.render(f'{self.m_id}', True, cfg.BLACK)
        self.updateSprite(cfg, robot_info.get("display_scale_factor"))

        self.direction = self.unitVec(self.target_position - self.m_position)
        self.next_direction = self.direction

        self.tunnel_rect = []

        self.fight_range = cfg.FIGHTTHRESHOLD
        self.passive_range = cfg.PASSIVETHRESHOLD
        self.detection_range = cfg.DETECTIONRANGE
    #end function



    def setConfig(self, cfg, k):
        #copies config parameters to the agents internal parameters
        self.m_id = cfg['ids'][k]
        self.aggression_level = cfg['aggressions'][k]
        self.speed = cfg['speeds'][k]
        self.aggression_type = cfg['aggression_types'][k]
        self.fight_range_max = cfg['fight_threshold_max'][k]
        self.passive_range_max = cfg['passive_threshold_max'][k]
        self.detection_range_max = cfg['detection_threshold_max'][k]
        return
    #end function



    def updateLog(self, time_now, food_collected_b, visited_home_b, stationary_b, tunnel_entry_b, tunnel_exit_b, success_passage, fail_passage):
        '''stores and updates useful counts about what the agent has done in the world
        '''
        L = self.log
        L.ticks_in_task_state[self.task_state] += 1
        L.ticks_in_social_state[self.social_state] += 1
        L.ticks_in_terrain_state[self.terrain_state] += 1
        if food_collected_b:
            L.n_visits_to_food += 1
        if visited_home_b:
            L.n_visits_to_home += 1
            L.n_t_visits_home.append(time_now)
        if stationary_b:
            L.n_ticks_not_moving += 1
        L.n_passages_through_tunnel_success += success_passage
        L.n_passages_through_tunnel_fail += fail_passage
        L.n_tunnel_entry += tunnel_entry_b
        L.n_tunnel_exit += tunnel_exit_b
        return
    #end function



    def printLog(self, cfg):
        '''useful for debugging'''
        print(f"Log for robot {self.m_id} \nMy speed is {self.speed}")
        self.log.printLog(cfg)
        return
    #end function



    def detectRobots(self, cfg, robots : pygame.sprite.Group(), detection_range : int) -> pygame.sprite.Group():
        '''
        Return the other robots which are within the sensor range AND in the direction the robot wants to go
            (we assume the robot can't see other robots behind it)
        '''
        CONE_OF_VISION = 3.14 / (180/5)
        #initialise the output
        self.robots_front.empty()
        self.robots_rear.empty()

        my_heading = self.target_position - self.m_position
        #calculation is centre to centre but we assume aggression range is measured between the outer edges
        detection_range = detection_range + 0.5*cfg.AGENT_SIZE

        #loop through each robot and test if it's within the cone of vision.
        #   first check if the robot is within a radial threshold
        #   then test if it's within an angular threshold
        distance2nearest_front = 6000
        distance2nearest_rear = 6000
        for robot in robots.sprites():
            if robot.m_id != self.m_id:
                heading2robot = robot.m_position-self.m_position
                #test radial threshold
                distance = abs(heading2robot[0])
                if distance < detection_range:
                    #test radial threshold
                    if np.sign(heading2robot[0])==np.sign(my_heading[0]):
                        self.robots_front.add(robot)
                        if distance < distance2nearest_front:
                            distance2nearest_front = distance
                    else:
                        self.robots_rear.add(robot)
                        if distance < distance2nearest_rear:
                            distance2nearest_rear = distance
        return distance2nearest_front, distance2nearest_rear
    #end function



    def isCollision(self, robots, velocity):
        collision_b = False
        velocity = np.squeeze(velocity)
        for robot in robots.sprites():
            if robot.m_id != self.m_id:
                #if the robots are on top of eachother at the current postion then don't count a collision
                # this can happen if the robots are pasing through eachother (in free space) and then overlap at the tunnel entrance/exit
                if robot.rect.colliderect(self.rect):
                    collision_b = False
                    return collision_b
                elif robot.rect.colliderect(self.rect.move(velocity[0],velocity[1])):
                    collision_b = True
                    return collision_b
        return collision_b
    #end function



    def isObstacleDetected(self, tunnel_rect, robots):
        #create a velocity obstacle equal to the space the robot will sweep through on its next update
        #TODO: COMPLETE CODE FOR THIS IF OBSTACLE DETECTION IS NEEDED
        new_centre = self.move()
        return



    def calcAggression(self, cfg, agg_type = []):
        if agg_type == cfg.AGGRESSION_TYPES['random']:
            import random
            aggression = random.randint(cfg.AGGRESSIONLIMITS[0],cfg.AGGRESSIONLIMITS[1]) + cfg.FIGHTTHRESHOLD
        else:
            aggression = self.aggression_level

        return aggression
    #end function



    def move(self, velocity, m_position) -> np.array:
        #calculate vector heading from current position to target
        new_position = m_position + velocity
        return np.squeeze(new_position)
    #end function



    def updateTaskState(self, cfg, home_rect, food_rect):
        #*********update its goal state*********
        #default is to maintain the same task state
        next_task_state = self.task_state
        next_target_position = self.target_position
        if self.task_state == cfg.FORAGING_STATES["going_home"]:
            home_b = home_rect.contains(self.rect)
            if home_b and self.has_food_b:
                next_task_state = cfg.FORAGING_STATES["finding_food"]
                next_target_position = np.asarray(food_rect.center)
                self.has_food_b = False
        
        elif self.task_state == cfg.FORAGING_STATES["finding_food"]:
            found_food_b = food_rect.contains(self.rect)
            if found_food_b and not self.has_food_b:
                next_task_state = cfg.FORAGING_STATES["going_home"]
                next_target_position = np.asarray(home_rect.center)
                self.has_food_b = True
        return next_task_state, next_target_position
    #end function           



    def updateTerrainState(self, cfg, tunnel_rects):
        #*******update its terrain state*********
        #default to not in a tunnel unless detected otherwise
        next_terrain_state = cfg.TERRAIN_STATES["none"]
        for r in tunnel_rects:
            if self.rect.colliderect(r):
                next_terrain_state = cfg.TERRAIN_STATES["tunnel"]
                #remember which tunnel the robot is in (or was last in)
                self.tunnel_rect = r
                break
        return next_terrain_state
    #end function    
      


    def closestRobot(self, robots):
        distance = 6000
        closest_robot = []
        for robot in robots:
            if robot.m_id !=self.m_id:
                d = abs(robot.m_position[0] - self.m_position[0])
                if d<distance:
                    distance = d
                    closest_robot = robot
        return closest_robot
    #end function
      


    def nearestAggression(self, robots):
        '''
        returns the aggression level of the closest robot
        '''
        return self.closestRobot(robots).aggression_level
    #end function      


   
    def distance2ClosestBrave(self, cfg, robots):
        d = float("inf")
        closest_brave_robot = []
        for robot in robots:
            if robot.social_state == cfg.SOCIAL_STATES['fight_brave']:
                foo = abs(self.m_position[0] - robot.m_position[0])
                if foo<d:
                    d = foo
                    closest_brave_robot = robot
        return d, closest_brave_robot
    #end function      



    def isOppositeDirection(self, robot):
        if np.sign(self.direction[0])==np.sign(robot.direction[0]):
            return False
        else:
            return True
    #end function      



    def isRobotBrave(self, cfg, robots):
        b = False
        if len(robots)>0:
            for robot in robots:
                if robot.social_state == cfg.SOCIAL_STATES['fight_brave']:
                    b = True
                    break
        return b
    #end function      



    def directionToRun(self, cfg, include_non_brave_b = True):
        #when first affraid, set the direction to run away from the nearest brave robot,
        #   if there isn't a brave robot then move away from the nearest robot.
        robots = self.robots_front

        _, closest_robot = self.distance2ClosestBrave(cfg, robots)
        afraid_direction = []
        if closest_robot:
            afraid_direction  = self.unitVec(self.m_position - closest_robot.m_position)
        elif include_non_brave_b:
            closest_robot = self.closestRobot(robots)
            #if affraid then move away from the closest robot
            afraid_direction  = self.unitVec(self.m_position - closest_robot.m_position)
        return afraid_direction
    #end function      



    def updateConflictList(self, cfg, robots, conflict_list, conflict_active_b):
        #for each detected robot, check if it's within fight range, in front of me and I'm in a tunnel
        # if it is, add it to the list of robots it's in conflict with 
        new_rival_b = False
        if self.terrain_state == cfg.TERRAIN_STATES["tunnel"]:
            for robot in robots:
                distance = abs(robot.m_position[0] - self.m_position[0])
                if ((distance < self.fight_range)):
                    if (robot not in conflict_list 
                            and robot.terrain_state == cfg.TERRAIN_STATES["tunnel"]
                            and self.isOppositeDirection(robot)):
                        conflict_list.add(robot)
                        new_rival_b = True

        #cycle through the current list and remove any robots which no longer meet the conditions for conflict
        #   This is based only on them being far enough away, it's tempting to remove robots which aren't in the tunnel as well?
        for robot in conflict_list:
            distance = abs(robot.m_position[0] - self.m_position[0])
            #the robot is out of range so remove it from the list
            if ((distance >= self.passive_range) 
                    and (robot in conflict_list)):
                conflict_list.remove(robot)

            elif (robot.terrain_state == cfg.TERRAIN_STATES["none"]):
                if self.social_state==cfg.SOCIAL_STATES["fight_affraid"] and not self.tunnel_rect.inflate(cfg.AGENT_SIZE*2,0).colliderect(robot.rect):
                    conflict_list.remove(robot)
                elif not self.social_state==cfg.SOCIAL_STATES["fight_affraid"]:
                    conflict_list.remove(robot)

        return conflict_list, new_rival_b
    #end function      
          


    def affraidState(self, cfg, distance2nearest_robot, conflict_active_b = True):
        """
        Returns:    next_social_state, 
                    next_state_entry_b,
                    next_aggression_level, 
                    next_conflict_list
        """

        next_aggression_level = self.aggression_level
        next_conflict_list = self.conflict_list.copy()
        next_social_state = self.social_state
        next_state_entry_b = self.state_entry_b

        robots = self.robots_front       

        #on state entry
        if self.state_entry_b == True:
            next_aggression_level = self.calcAggression(cfg, self.aggression_type)
            #DEBUG
            #print(f"Robot{self.m_id} has chosen aggression {next_aggression_level}")
            next_state_entry_b = False
            self.time_in_state=0

        #in state (this will force the robot to affraid for at least 1 tick) 
        else:      
            #test if the robot should re-enter the affraid state
            new_rival_b = False
            tie_b = False
            go_brave_b = False

            #update conflict list
            next_conflict_list, new_rival_b = self.updateConflictList(cfg, robots, next_conflict_list, conflict_active_b)

            #if the list is empty then goto navigate  
            # BYPASSED, moved to the last condition to check rather than the first
            #TODO: Tidy up this section
            if 1==2:#not next_conflict_list and self.time_in_state > MIN_TIME_FOR_AFFRAID_UNLESS_BRAVE:
                next_social_state = cfg.SOCIAL_STATES['navigate']
                next_state_entry_b = True  

            #check if go brave
            else:
                for robot in next_conflict_list:
                        #if it's a tie for aggression then goto affraid
                        if (robot.aggression_level == next_aggression_level):
                            #re-enter the affraid state and try again
                            # this is intended to resolve sitations where two robots randomly pick the same number
                            tie_b = True
                            #do this to force the agent to re-enter the state
                            next_social_state = cfg.SOCIAL_STATES['fight_affraid']
                            next_state_entry_b == True                                                  
                #test if robot should become brave
                #   the robot can't become brave if a previous condition has forced it to re-enter the affraid state
                if not new_rival_b and not tie_b:
                    max_aggression = float("inf")
                    for robot in next_conflict_list:
                        if robot.aggression_level < max_aggression:
                            max_aggression = robot.aggression_level
                    if next_aggression_level < max_aggression:
                        #I should be brave
                        go_brave_b = True
                        next_social_state = cfg.SOCIAL_STATES['fight_brave']
                        next_state_entry_b = True

                #if conflict isn't active then goto navigate
                if not go_brave_b and not conflict_active_b and not next_conflict_list:
                    next_social_state = cfg.SOCIAL_STATES['navigate']
                    next_state_entry_b = True             

        self.time_in_state+=1
        return (next_social_state, next_state_entry_b, next_aggression_level, next_conflict_list)
    #end function



    def braveState(self,cfg, distance2nearest_robot, conflict_active_b = True):
        """
        Returns:    next_social_state, 
                    next_state_entry_b,
                    next_aggression_level, 
                    next_conflict_list
        """
        next_aggression_level = self.aggression_level
        next_conflict_list = self.conflict_list.copy()
        next_social_state = self.social_state
        next_state_entry_b = self.state_entry_b

        new_rival_b = False
        tie_b = False

        robots = self.robots_front

        #on state entry
        if self.state_entry_b == True:
            next_time_in_brave = 0
            next_state_entry_b = False
        
        #in state
        else:
            #update conflict list
            next_conflict_list, new_rival_b = self.updateConflictList(cfg, robots, next_conflict_list, conflict_active_b)
                               
            #if the list is empty then goto navigate    
            if not next_conflict_list:
                next_social_state = cfg.SOCIAL_STATES['navigate']
                next_state_entry_b = True  

            #if conflict isn't active then goto navigate
            elif not conflict_active_b:
                next_social_state = cfg.SOCIAL_STATES['navigate']
                next_state_entry_b = True  
            
            #there's only pre-existing robots on the list and conflict is active      
            else:
                # check each robot on the list and check if a state change is needed
                for robot in next_conflict_list:
                    #if it's a tie for aggression then goto affraid
                    if (robot.aggression_level == next_aggression_level):
                        #re-enter the affraid state and try again
                        # this is intended to resolve sitations where two robots randomly pick the same number
                        tie_b = True
                        #do this to force the agent to re-enter the state
                        next_social_state = cfg.SOCIAL_STATES['fight_affraid']
                        next_state_entry_b = True
                    # a different robot on the aggression list has become brave
                    # a new robot has joined the list and the robot is no longer the bravest
                    # state entry is false so it WONT get a new aggression_level when it becomes afraid
                    # note the robot must pass through afraid to reach brave so it will have had a value set
                    elif robot.aggression_level < next_aggression_level:
                        next_social_state = cfg.SOCIAL_STATES['fight_affraid']
                        next_state_entry_b = False  

        return (next_social_state, next_state_entry_b, next_aggression_level, next_conflict_list)
    #end function



    def navigateState(self, cfg, distance2nearest_robot, conflict_active_b = True):
        """
        Returns:    next_social_state, 
                    next_state_entry_b,
                    next_aggression_level, 
                    next_conflict_list
        """
        next_aggression_level = self.aggression_level
        next_conflict_list = self.conflict_list.copy()
        next_social_state = self.social_state
        next_state_entry_b = self.state_entry_b
        
        robots = self.robots_front

        #on state entry
        if self.state_entry_b == True:
            next_state_entry_b = False
            next_conflict_list.empty()
        #in state
        else:

            #update conflict list
            next_conflict_list, new_rival_b = self.updateConflictList(cfg, robots, next_conflict_list, conflict_active_b)
            
            #goto affraid if there's at least one rival in the list
            if next_conflict_list:
                next_social_state = cfg.SOCIAL_STATES['fight_affraid']
                next_state_entry_b = True
        
        return (next_social_state, next_state_entry_b, next_aggression_level, next_conflict_list)
    #end function

        

    def updateSocialState(self, cfg, distance2nearest_robot, conflict_active_b = True) -> None:       
         #******update its social state************
        next_social_state = self.social_state
        next_state_entry_b = self.state_entry_b
        next_time_in_brave = self.time_in_brave
        next_aggression_level = self.aggression_level
        next_conflict_list = self.conflict_list.copy()

        new_rival_b = False
        tie_b = False
        go_brave_b = False

        if cfg.NO_COLLISONS_B:
            return next_social_state, next_aggression_level, next_state_entry_b, next_time_in_brave, next_conflict_list

        if self.social_state == cfg.SOCIAL_STATES['navigate']:
            next_social_state, next_state_entry_b, next_aggression_level, next_conflict_list = self.navigateState(cfg, distance2nearest_robot,conflict_active_b)
            
        elif self.social_state == cfg.SOCIAL_STATES['fight_affraid']:
            next_social_state, next_state_entry_b, next_aggression_level, next_conflict_list = self.affraidState(cfg, distance2nearest_robot,conflict_active_b)
                      
        elif self.social_state == cfg.SOCIAL_STATES['fight_brave']:
             next_social_state, next_state_entry_b, next_aggression_level, next_conflict_list = self.braveState(cfg, distance2nearest_robot,conflict_active_b)    
        
        else: #panic
            #TODO: ADD PANIC STATE IF NEEDED
            pass

        return next_social_state, next_aggression_level, next_state_entry_b, next_time_in_brave, next_conflict_list
    #end function



    def isEnteredTunnel(self, cfg, tunnel_rect):
        '''Returns:
        has_entered_tunnel_b: Boolean
        tunnel_size: either cfg.TUNNEL_STATES['ENL'] (entered tunnel left) or cfg.TUNNEL_STATES['ENR'] (entered tunnel right)
        '''
        tunnel_side = ""
        has_entered_tunnel_b = False
        if self.terrain_state == cfg.TERRAIN_STATES['none'] and self.next_terrain_state == cfg.TERRAIN_STATES['tunnel']:
            has_entered_tunnel_b = True
            if self.rect.left < tunnel_rect.left:
                tunnel_side = cfg.TUNNEL_STATES['ENL']
            else:
                tunnel_side = cfg.TUNNEL_STATES['ENR']
        return has_entered_tunnel_b, tunnel_side
    #end function



    def isExitTunnel(self, cfg, tunnel_rect):
        '''Returns:
        has_exit_tunnel_b: Boolean
        tunnel_size: either cfg.TUNNEL_STATES['EXL'] (exit tunnel left) or cfg.TUNNEL_STATES['EXR'] (exit tunnel right)
        '''
        tunnel_side = ""
        has_exit_tunnel_b = False
        if self.terrain_state == cfg.TERRAIN_STATES['tunnel'] and self.next_terrain_state == cfg.TERRAIN_STATES['none']:
            has_exit_tunnel_b = True
            if self.rect.left < tunnel_rect.left:
                tunnel_side = cfg.TUNNEL_STATES['EXL']
            else:
                tunnel_side = cfg.TUNNEL_STATES['EXR']
        return has_exit_tunnel_b, tunnel_side
    #end function



    def updateTunnelPassageCount(self, cfg, tunnel_rect):

        passage_success = 0
        passage_fail = 0
        new_tunnel_state = self.tunnel_state
        tunnel_entry_b = False
        tunnel_exit_b = False

        if (self.terrain_state == cfg.TERRAIN_STATES['tunnel'] and 
                (self.social_state == cfg.SOCIAL_STATES['fight_affraid'] or self.social_state == cfg.SOCIAL_STATES['fight_brave'])):
            new_tunnel_state[cfg.TUNNEL_STATES['conflict']] = 1

        [entered_tunnel_b, side] = self.isEnteredTunnel(cfg, tunnel_rect)
        if entered_tunnel_b:
            new_tunnel_state[side]=1
            tunnel_entry_b = True
            
        else:
            [exit_tunnel_b, side] = self.isExitTunnel(cfg, tunnel_rect)
            if exit_tunnel_b:
                tunnel_exit_b = True
                #if the agent entered the left and is exiting the right then record a success if it also encountered a conflict while in the tunnel
                if ( (side==cfg.TUNNEL_STATES['EXR'] and self.tunnel_state[cfg.TUNNEL_STATES['ENL']]==1) or
                    (side==cfg.TUNNEL_STATES['EXL'] and self.tunnel_state[cfg.TUNNEL_STATES['ENR']]==1) ):
                    if self.tunnel_state[cfg.TUNNEL_STATES['conflict']]==1:
                        passage_success = 1
                elif ( (side==cfg.TUNNEL_STATES['EXR'] and self.tunnel_state[cfg.TUNNEL_STATES['ENR']]==1) or
                    (side==cfg.TUNNEL_STATES['EXL'] and self.tunnel_state[cfg.TUNNEL_STATES['ENL']]==1) ):
                     if self.tunnel_state[cfg.TUNNEL_STATES['conflict']]==1:
                        passage_fail = 1
                #reset the state when robot exits tunnel
                new_tunnel_state = np.zeros(len(cfg.TUNNEL_STATES))
        return passage_success, passage_fail, new_tunnel_state, tunnel_entry_b, tunnel_exit_b
    #end function



    def act(self,cfg, social_state, terrain_state, target_position):
        ''' The main dynamics function which takes the current sensor state and turns it into a direction and speed to move.  Call once per simulation time step
        '''  
        #create a copy of the other robots the agent can see (at the last time step)
        robots = self.robots

        #Remember the direction moved on the last time step
        # this is a hack to ensure direction is always updated on the next tick regardless of whether the updates are sync or async
        # i.e. self.direction is the direction at t-1
        self.direction = self.next_direction

        #RESOLVE THE DIRECTION TO MOVE
        #default direction is towards the current target in the navigate and brave states
        direction = self.unitVec(target_position - self.m_position)
        distance2closest_brave, closest_brave_robot = self.distance2ClosestBrave(cfg, robots)

        #create an early return if collisions are turned off
        if cfg.NO_COLLISONS_B:
            return direction * self.speed * cfg.DT

        elif social_state == cfg.SOCIAL_STATES["fight_affraid"]:
            #if it's only just moved in to the affraid state then don't move
            if self.time_in_state<=1:
                return 0
            else:            
                #if it's affraid and can see a brave robot (either forward or backwards) then run away from it
                if closest_brave_robot!=[] and distance2closest_brave <= cfg.AGENT_SIZE*cfg.N_ROBOTS:
                    direction = -self.unitVec(closest_brave_robot.m_position - self.m_position)  
                else: 
                    #if it's affraid but can't see a brave robot then default to moving away from its target
                    direction = -self.unitVec(target_position - self.m_position)

        #self.robots_front are the robots in the direction towards its current goal NOT the direction its moving
        #   so if it's direction of travel is away from it's goal (because it's affraid) we need to use self.robots_rear to check
        #   if the way is clear
        #TODO find a neater way
        if np.sign(direction[0]) == np.sign(target_position[0] - self.m_position[0]):
             robots_ahead = self.robots_front
        else:
             robots_ahead = self.robots_rear

        closest_robot = self.closestRobot(robots_ahead)
     
        #set the agent's speed
        speed = self.speed
        if closest_robot != []:
            #if not in a tunnel then always move at normal speed
            if terrain_state==cfg.TERRAIN_STATES['none']:
                speed = self.speed
            #if the agents are already on top of eachother, can occur at tunnel entrance if one was overtaking the other
            elif abs(closest_robot.m_position[0] - self.m_position[0]) < 0.5 *  cfg.AGENT_SIZE:
                #ignore the collision
                speed = self.speed
            #if the distance to the closest robot is smaller than the distance the robot would move to then don't move
            # i.e. if it's in a tunnel, then don't move if it's movement would collide with the nearest detected robot
            elif (abs(closest_robot.m_position[0] - self.m_position[0]) - cfg.AGENT_SIZE) <= (self.speed*cfg.DT):
                speed = 0

        #remember the direction for the current time step
        self.next_direction = direction

        #do some logging
        if speed == 0:
            self.time_stationary += 1
        else:
            self.time_stationary = 0

        return direction * speed * cfg.DT
    #end function



    def updateRanges(self, cfg):
        if self.time_stationary >=1:
            self.fight_range += 5
            self.passive_range += 5
            self.detection_range += 5
        else:
            self.fight_range = max([cfg.FIGHTTHRESHOLD, self.fight_range-2])
            self.passive_range = max([cfg.PASSIVETHRESHOLD, self.passive_range-2])
            self.detection_range = max([cfg.DETECTIONRANGE, self.detection_range-2])
            #caps the detection range from getting too large
            self.detection_range = min([self.detection_range, self.detection_range_max])
            self.passive_range = min([self.passive_range, self.passive_range_max])
            self.fight_range = min([self.fight_range, self.fight_range_max])
        return
    #end function



    def updateNextTS(self, cfg, home_rect, food_rect, tunnel_rects, robots):
        """
        The main function which causes the agent to "Sense,Plan,Act".  Call once per simulation time step
        Arugments: robots - all robots in the world
        """
        #Sense
        [d2nearest_front, d2nearest_rear] = self.detectRobots(cfg, robots, self.detection_range)

        #create a group of robots which doesn't include the itself
        self.robots.empty()
        self.robots.add([self.robots_front, self.robots_rear])

        next_terrain_state = self.updateTerrainState(cfg, tunnel_rects)

        #config can override collisions regardless of the terrain type the agent is in
        if cfg.NO_COLLISONS_B:
            collisions_b = False
        else:
            #if in the tunnel then collisions are on
            if next_terrain_state == cfg.TERRAIN_STATES['tunnel']:
                collisions_b = True
            else:
                collisions_b = False
                
        #plan by updating state.
        # is the agent moving towards home or food??
        next_task_state, next_target_position = self.updateTaskState(cfg, home_rect, food_rect)       
        
        #update the social state
        # should the agent be brave, affraid or navigating
        d = min([d2nearest_front,d2nearest_rear])
        next_social_state, next_aggression_level, next_state_entry_b, next_time_in_brave, next_conflict_list = self.updateSocialState(cfg, d, collisions_b)

        #update the sensor ranges, these grow if the robot hasn't moved
        self.updateRanges(cfg)
        
        #update the direction and speed the agent should be moving
        next_speed = self.act(cfg, next_social_state, next_terrain_state, next_target_position)

        #update where in the world the agent should be
        next_position = self.move(next_speed, self.m_position)

        #store the state at t+1
        self.next_task_state = next_task_state
        self.next_target_position = next_target_position
        self.next_terrain_state = next_terrain_state
        self.next_social_state = next_social_state
        #self.next_speed = next_speed        
        self.next_position = next_position
        self.next_state_entry_b = next_state_entry_b
        self.next_time_in_brave =  next_time_in_brave 
        self.next_aggression_level = next_aggression_level
        self.next_conflict_list = next_conflict_list.copy()

        return
    #end function



    def advanceTime(self, cfg, time_now, tunnel_rects):
        '''Function which copies the output of "updateNextTS()" to the current time step.
        Useful for switching between asynchronous and sychronous update methods
        '''

        #log the meaning of state changes on the task
        if np.array_equal(self.next_position, self.m_position):
            not_move_b = True
        else:
            not_move_b = False
        self.setPosition(self.next_position)

        if self.task_state == cfg.FORAGING_STATES['finding_food'] and self.next_task_state == cfg.FORAGING_STATES['going_home']:
            collected_food_b = True
        else:
            collected_food_b = False

        if self.task_state == cfg.FORAGING_STATES['going_home'] and self.next_task_state == cfg.FORAGING_STATES['finding_food']:
            returned_food_b = True
        else:
            returned_food_b = False

        [success_passage, fail_passage, new_tunnel_state, tunnel_entry_b, tunnel_exit_b] = self.updateTunnelPassageCount(cfg, self.tunnel_rect)
        
        #after updating the counts, clear the tunnel state
        self.tunnel_state = new_tunnel_state
        
        #Copy the state at t+1 into t
        self.task_state  = self.next_task_state 
        self.target_position = self.next_target_position 
        self.terrain_state = self.next_terrain_state 
        self.social_state = self.next_social_state 
        #self.speed = self.next_speed      
        self.m_position = self.next_position
        self.state_entry_b = self.next_state_entry_b
        self.time_in_brave =  self.next_time_in_brave 
        self.aggression_level = self.next_aggression_level
        self.conflict_list = self.next_conflict_list.copy()
        #update the visual representation  
        self.updateSprite(cfg, 1)

        #update the log
        self.updateLog(time_now, collected_food_b, returned_food_b, not_move_b, tunnel_entry_b, tunnel_exit_b, success_passage, fail_passage)
        return collected_food_b
    #end function



    # pygame already has a function for this
    # def isContained(self, rect_outer, rect_inner):
    #     b_h = (rect_inner.left > rect_outer.left) and (rect_inner.right < rect_outer.right)
    #     b_w = (rect_outer.bottom > rect_inner.bottom) and (rect_outer.top < rect_inner.top)
    #     return (b_h and b_w)
    # #end function


    def unitVec2d(self,V):
        ''' UNITVEC2D Converts an input vector in to a unit vector
        Function accepts a list of vectors in row format [xi,yi]
        '''
        V = np.atleast_2d(V)
        sz = V.shape
        V_normalised = np.zeros(sz)

        #convert to row vectors if needed
        if sz[0] == 2 and sz[1] == 1:
            V = np.transpose(V)
            V_normalised = np.transpose(V_normalised)

        mag = np.linalg.norm(V, axis=1)
        idx = mag!=0

        #if any of the vectors are not zero then convect them to unit vectors
        if np.any(idx):
            V_normalised[idx,:] = V[idx,:]/mag[idx]
        
        return V_normalised
    #end function



    def unitVec(self,V):
        ''' UNITVEC Opperates only on the x direction and sets the y to zero!!!
        This is A LOT faster than unitVec2d if only 1 dimension is being used
        '''
        V = np.squeeze(V)
        V_normalised = np.array([np.sign(V[0]), 0])       
        return V_normalised
    #end function



    def updateSprite(self, cfg, scale_factor):
        ''' set colour of the robot based on its social state
        #   red or yellow: it's interacting another robot
        #   green: it's not interacting
        '''
        # places a number on the image of the robot (moved code out of this function)
        # font = pygame.font.SysFont(None, cfg.AGENT_SIZE)
        # font_image = font.render(str(self.m_id), True, cfg.BLACK)

        if cfg.DRAWSCREEN:        
            if self.sprite_images:
                if self.social_state == cfg.SOCIAL_STATES["fight_brave"]:
                    self.setImage(self.sprite_images['r'])
                elif self.social_state == cfg.SOCIAL_STATES["fight_affraid"]:
                    self.setImage(self.sprite_images['y'])
                else:
                    self.setImage(self.sprite_images['g'])
            else:
                if self.social_state == cfg.SOCIAL_STATES["fight_brave"]:
                    if self.sprite_images:
                        colour = self.sprite_images['r']
                    else:
                        colour = cfg.RED
                elif self.social_state == cfg.SOCIAL_STATES["fight_affraid"]:
                    colour = cfg.YELLOW
                else:
                    colour = cfg.GREEN

                img = pygame.Surface((cfg.AGENT_SIZE,cfg.AGENT_SIZE))

                img.fill(colour)

                img.blit(self.font_img, (2,2))
                # img.blit(font_image, img.get_rect().topleft)
                self.setImage(img)

        #move the agent's image to align with its position in the screen coordinate frame
        pos_in_screen_coords = self.m_position * scale_factor
        self.setSpritePosition(pos_in_screen_coords)
        return
    #end function
