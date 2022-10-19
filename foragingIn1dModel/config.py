class Config:
    def __init__(self) -> None:       
        #Map words to numbers
        self.FORAGING_STATES = {"going_home" : 0, "finding_food" : 1}
        self.SOCIAL_STATES = {"navigate" : 0, "panic" : 1, "fight_brave" : 2, "fight_affraid" : 3}
        self.TERRAIN_STATES = {"none" : 0, "tunnel" : 1}
        
        #these are the types of conflict resolution mechanism.
        # random : Arbitrary (Transient)
        # assigned_increasing : Fittest Last or Biggest Range Last (note the order of the speeds or senor ranges assigned to the agents)
        # assigned_decreasing : Fittest First or Biggest Range First 
        # random_preassigned : Arbitrary (Fixed)
        self.AGGRESSION_TYPES = {"random": 0, "assigned_increasing": 1, "assigned_decreasing": 2 , "random_preassigned": 3,
                                "slowest_and_biggest_range_first": 4, "fastest_and_biggest_range_first" : 5,
                                "slowest_and_smallest_range_first" : 6, "fastest_and_smallest_range_first" : 7}
        
        self.UPDATE_TYPES = {"sync": 0, "async" : 1, "async_reverse" : 2, "async_random" : 3}
        self.BRAVE_MECHANICS = {"original" : 0, "new": 1}
        self.TUNNEL_STATES = {"ENL" : 0, "ENR" : 1,"EXL" : 2,"EXR" : 3, "conflict": 4}
        
        self.IMAGE_NAMES = ['train','convertable','bev']
        self.IMAGE_COLOURS = ['g','y','r']

        #define some useful colours
        self.BLACK = 0, 0, 0
        self.WHITE = 255, 255, 255
        self.RED = 255, 0, 0
        self.GREEN = 0, 255, 0
        self.BLUE = 0, 0, 255
        self. ORANGE = 255, 165, 0
        self.YELLOW = 255,255,0
        self.ERANGE = [self.RED,self.YELLOW, self.ORANGE, self.GREEN, self.GREEN]

        #user settings for the simulation
        self.DRAWSCREEN = True #set true to visualise the simulation (simulation runs faster when this is set to False)
        self.UPDATETYPE = self.UPDATE_TYPES["async_random"] #Recommended to leave this at async_random
        self.BRAVE_TRANSITION_MECHANIC = self.BRAVE_MECHANICS["new"] #Recommended to leave this as "new"
        self.aggression_type = self.AGGRESSION_TYPES["assigned_decreasing"] #changes the conflict resolution mechanism
        self.USE_CUSTOM_SPRITES = False #set true to change from squares to a user loaded image (experimental!)
        self.NO_COLLISONS_B = False #set true to turn off collisions, agents will pass through eachother regardless of the terrain

        self.SQUARE_SIZE = 10
        self.TUNNEL_WIDTH = 300
        self.AGENT_SIZE = 10 
        self.N_ROBOTS = 5
        self.TIME_LIMIT = 150*10 #the total length of the simulation!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.TICK_RATE = 50 #the speed of the simulation, setting a lower number slows it down (useful when DRAWSCREEN is True).  Has no effect when DRAWSCREEN is False
        self.RES = (1280,720) #the size of the window when DRAWSCREEN is True
        self.HOME_POSITION = (40+50,360)
        
        self.EXPERIMENT_NUMBER = 1
        self.DT = 0.5 #time step interval of the simulation (effectively this just scales TIME_LIMIT by 1/DT)
        self.N_REPEATS = 1 #How many times to repeate the simulation.  Each simulation is the same except agents start in different positions along the route
        self.DV = 5 #set to either 5 or 10, changes the range of speeds in the population (the level of disparity between the agents)

        #these are set by generateConfig()
        self.DETECTIONRANGE = 0
        self.FIGHTTHRESHOLD = 0
        self.PASSIVETHRESHOLD = 0

        self.DETECTION_RANGE_LIMIT = 350 #needed to stop robots seeing two tunnels
        
        self.AGGRESSIONLIMITS = (1,49)
        self.AGGRESSION_STEPS = 10

        self.AVG_POPULATION_SPEED = 50 #here for information, not sure it's actually used??

        self.SEED = 10 #used for generating random numbers
        self.RAND_SPEEDS_B = False #set true to assign a random speed (unordered) to each agent
        self.RAND_FIGHT_RANGE_B = False #set true to assign a random conflict range (unordered) to each agent

        self.SPEEDS = {5:  {1: [50],
                            2: [47.5, 52.5],
                            3: [45, 50, 55],
                            4: [42.5, 47.5, 52.5, 57.5],
                            5: [40, 45, 50, 55, 60],
                            6: [37.5, 42.5, 47.5, 52.5, 57.5, 62.5],
                            7: [35,	40,	45,	50,	55,	60,	65],
                            8: [32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5],
                            9: [30, 35, 40, 45, 50, 55, 60, 65, 70]
                        },
                10 :  {     1: [50],
                            2: [45,55],
                            3: [40,50,60],
                            4: [35, 45, 55, 65],
                            5: [30, 40, 50, 60, 70],
                            6: [25, 35, 45, 55, 65, 75],
                            7: [20, 30, 40, 50, 60, 70, 80],
                            8: [15, 25, 35, 45, 55, 65, 75, 85],
                            9: [10, 20, 30, 40, 50, 60, 70, 80, 90]
                        }
                }
        #structure to hold settings for individual agents
        self.ROBOTS = {}

    def generateConfig(self):
        '''Run to generate elements of the config which are dependent on simulation parameters set by the user'''

        import numpy as np
        multiplier = np.arange(2,self.N_ROBOTS+2)

        # #auto generating config
        if self.aggression_type == self.AGGRESSION_TYPES["assigned_increasing"]:
            aggressions = [(i * self.AGGRESSION_STEPS + self.FIGHTTHRESHOLD) for i in range(1, self.N_ROBOTS+1, +1)]
   
        elif self.aggression_type == self.AGGRESSION_TYPES["assigned_decreasing"]:
            aggressions = [(i * self.AGGRESSION_STEPS + self.FIGHTTHRESHOLD) for i in range(self.N_ROBOTS+1, 1, -1)]
   
        elif self.aggression_type ==self.AGGRESSION_TYPES["random_preassigned"]:
            import random
            #upper range is +1 robots because range doesn't include the top step
            aggressions = random.sample(range(self.AGGRESSION_STEPS+self.FIGHTTHRESHOLD, (self.N_ROBOTS+1) * self.AGGRESSION_STEPS +self.FIGHTTHRESHOLD, self.AGGRESSION_STEPS), self.N_ROBOTS)
   
        elif self.aggression_type ==self.AGGRESSION_TYPES["slowest_and_biggest_range_first"]:
            aggressions = [(i * self.AGGRESSION_STEPS + self.FIGHTTHRESHOLD) for i in range(1, self.N_ROBOTS+1, +1)]
            multiplier = np.arange(self.N_ROBOTS+1,1,-1)
        
        elif self.aggression_type ==self.AGGRESSION_TYPES["fastest_and_biggest_range_first"]:
            aggressions = [(i * self.AGGRESSION_STEPS + self.FIGHTTHRESHOLD) for i in range(self.N_ROBOTS+1, 1, -1)]
            multiplier = np.arange(2,self.N_ROBOTS+2)
        
        elif self.aggression_type ==self.AGGRESSION_TYPES["slowest_and_smallest_range_first"]:
            aggressions = [(i * self.AGGRESSION_STEPS + self.FIGHTTHRESHOLD) for i in range(1, self.N_ROBOTS+1, +1)]
            multiplier = np.arange(2,self.N_ROBOTS+2)
        
        elif self.aggression_type ==self.AGGRESSION_TYPES["fastest_and_smallest_range_first"]:
            aggressions = [(i * self.AGGRESSION_STEPS + self.FIGHTTHRESHOLD) for i in range(self.N_ROBOTS+1, 1, -1)]
            multiplier = np.arange(self.N_ROBOTS+1,1,-1)
        else:
            #random case just sets these to 0 because they're randomly set during the run for each conflict
            aggressions = [0 for _ in range(0,self.N_ROBOTS)]
        
        if self.EXPERIMENT_NUMBER == 1:
            multiplier = np.ones(self.N_ROBOTS)
            detection_threshold_max = multiplier * self.DETECTION_RANGE_LIMIT
            passive_threshold_max = multiplier * (detection_threshold_max - 1 * self.AGENT_SIZE)  
            fight_threshold_max = multiplier * (passive_threshold_max - 2 * self.AGENT_SIZE)
        elif self.EXPERIMENT_NUMBER == 2:
            fight_threshold_max = multiplier * self.AGENT_SIZE
            passive_threshold_max = fight_threshold_max + 2 * self.AGENT_SIZE
            detection_threshold_max = passive_threshold_max + 1 * self.AGENT_SIZE

        if self.RAND_FIGHT_RANGE_B:
            multiplier = np.random.permutation(multiplier).tolist()
        
        speeds = self.SPEEDS[self.DV][self.N_ROBOTS]
        speeds = [s/5 for s in speeds]
        if self.RAND_SPEEDS_B:
            speeds = np.random.permutation(speeds).tolist()

        self.ROBOTS = {  "ids":  [i+1 for i in range(0,self.N_ROBOTS)], 
                    "speeds": speeds, 
                    "aggressions": aggressions,
                    "aggression_types": [self.aggression_type for _ in range(0,self.N_ROBOTS)],
                    "fight_threshold_max": fight_threshold_max.tolist(),
                    "passive_threshold_max": passive_threshold_max.tolist(),
                    "detection_threshold_max": detection_threshold_max.tolist()
                }

        self.FIGHTTHRESHOLD = self.AGENT_SIZE
        self.PASSIVETHRESHOLD = self.FIGHTTHRESHOLD + 2 * self.AGENT_SIZE
        self.DETECTIONRANGE = self.PASSIVETHRESHOLD + 1 * self.AGENT_SIZE