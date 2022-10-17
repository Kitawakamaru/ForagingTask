import pygame, sys
import Robot as Robot
import numpy as np
import random

def createStartScreen():
    #setup the screen
    return pygame.display.set_mode((1280,720))


def createAgents(cfg, group, number):
    ''' Creates an agent 
    cfg: a simulation config object
    group: a pygame sprite group which the new agent will belong to
    number: the number of agents to create
    by default, all agents are created at cfg.HOME_POSITON'''
    for i in range (number):
        #create a robot at the home position with an initial visualisation of a green square
        robot = Robot.Robot(cfg, cfg.HOME_POSITION, 10*i)
        img = pygame.Surface((cfg.AGENT_SIZE,cfg.AGENT_SIZE))
        img.fill(cfg.GREEN)
        robot.setImage(img)
        robot.setConfig(cfg.ROBOTS, i)
        group.add(robot)

    return

def xStartPositions(n_robots, pmin, pmax, robot_size = 1):
    '''generate random points along a line
    n_robots: the number of points to generate
    pmin to pmax: the range over which to generate the points
    robot_size: the minimum interval between points'''
    import random
    return random.sample(range(pmin,pmax,robot_size),n_robots)


class obstacle(pygame.sprite.Sprite):
    def __init__(self, left, top, width, height, colour):
        '''creates a static rectangular entity which can be visualised in the world
        left, top: the coordinates of the top left point of a rectangle
        width, height: the dimensions of the entity'''
        super().__init__()
        img = pygame.Surface((width,height))
        img.fill(colour)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top


def loadImages(IMAGE_NAMES, IMAGE_COLOURS, image_size):
    '''Loads a set of images and returns them as a dictionary of images
    This wasn't used in the experiment and is for (fun) test purposes only!!!!
    There must be 3 images (green, yellow, red for each image)
    '''
    images = {}
    IMAGE_NAMES = ['train','convertable','bev']
    IMAGE_COLOURS = ['g','y','r']
    import os.path
    for img_name in IMAGE_NAMES:
        if img_name not in images.keys():
            images[img_name] = {}
            
        for colour in (IMAGE_COLOURS):
            fname = img_name + '_' + colour + '.bmp'
            fpath = os.path.join('images', fname)
            img = pygame.image.load(fpath).convert_alpha()
            img = pygame.transform.scale(img, image_size)
            images[img_name][colour] = img 
    return images


def main(cfg=[]) -> None:
    ''' runs the simulation using the supplied config
    If no config is supplied then it uses config.py

    Returns:
    session_id : a unique identifier for the run
    header: the headings of the rows used in data
    data_all: a data structure for the simulation logs
    ticks: the number of ticks completed by the simulation.
    '''

    #import config as cfg
    if cfg == []:
        import config
        cfg = config.Config()
        cfg.generateConfig()
 
    #setup the screen to some default
    if cfg.DRAWSCREEN:
        screen = createStartScreen()

    #start pygame
    pygame.init()

    #create the clock to track time
    clock = pygame.time.Clock()

    #create a container for the agents
    agents = pygame.sprite.Group()

    #create a container for the obstacles
    obstacles = pygame.sprite.Group()  

    #Only look for a quit event, no other user input
    if cfg.DRAWSCREEN:
        pygame.event.set_allowed([pygame.QUIT])
    
    #create the agents
    createAgents(cfg, agents, cfg.N_ROBOTS)

    #load images for the agents
    if cfg.USE_CUSTOM_SPRITES:
        images = loadImages(cfg.IMAGE_NAMES, cfg.IMAGE_COLOURS, (cfg.AGENT_SIZE, cfg.AGENT_SIZE))
        
        #assign the images to the robots
        for i,robot in enumerate(agents):
            robot.sprite_images = images[cfg.IMAGE_NAMES[i]]

    #create two identical tunnels whose left hand coordinate in the x axis is given as a list in tunnel_left
    tunnel_width = cfg.TUNNEL_WIDTH
    tunnel_height = 100
    tunnel_gap=cfg.AGENT_SIZE
    tunnel_top = 360-round(tunnel_gap/2)-tunnel_height
    tunnel_left = [140+150-round(tunnel_width/2),
    140+700+50-round(tunnel_width/2)]
    tunnel_rect = []
    for left_coord in tunnel_left:
        #create the top rectangle of the tunnel
        tunnel = obstacle(left_coord, tunnel_top, tunnel_width, tunnel_height, cfg.RED)
        obstacles.add(tunnel)
        #create the bottom rectangle of the tunnel
        tunnel = obstacle(left_coord, tunnel_top+tunnel_height+tunnel_gap, tunnel_width, tunnel_height, cfg.RED)
        obstacles.add(tunnel)
        #create a collision object for the tunnel
        tunnel_rect.append(pygame.Rect(left_coord, tunnel_top, tunnel_width,  2 * tunnel_height + tunnel_gap))

    #create the home and food locations
    base_rect_height = 200
    base_rect_width = 20 
    home_rect = pygame.Rect(0,360-round(base_rect_height/2),base_rect_width,base_rect_height)
    food_rect = pygame.Rect(cfg.RES[0]-0-base_rect_width,360-round(base_rect_height/2),base_rect_width,base_rect_height)

    #set the agent initial conditions
    pstart = xStartPositions(cfg.N_ROBOTS, home_rect.right + cfg.AGENT_SIZE, food_rect.left - cfg.AGENT_SIZE, cfg.AGENT_SIZE+5)
    for i,robot in enumerate(agents):
        goto_food_b = random.random()>0.5
        robot.initialise(cfg,  {"home_position": np.asarray(home_rect.center),
                "food_position": np.asarray(food_rect.center), 
                "start_position":np.asarray(home_rect.center) + np.asarray([pstart[i], 0]),
                "target_position": food_rect.center if goto_food_b else home_rect.center,
                "starting_state": cfg.FORAGING_STATES["finding_food"] if goto_food_b else cfg.FORAGING_STATES["going_home"],
                "display_scale_factor": 1,
                "tunnel_rect": tunnel_rect})

    #initialise a counter to track game time
    ticks = 0
    food_last_collected_on_tick = 0
    stuck_b = False

    #run the simulation time loop
    while ticks<cfg.TIME_LIMIT and not stuck_b:
        #Handle the event queue
        if cfg.DRAWSCREEN:
            for event in pygame.event.get():
                # exit cleanly if user closes the window
                if event.type == pygame.QUIT:
                    sys.exit()           
        
        food_collected_in_tick_b = False

        #update the agents
        if cfg.UPDATETYPE == cfg.UPDATE_TYPES['async_reverse']:
            agents_itter = reversed(agents.sprites())
        elif cfg.UPDATETYPE == cfg.UPDATE_TYPES['async']:
            agents_itter = agents.sprites()
        elif cfg.UPDATETYPE == cfg.UPDATE_TYPES['async_random']:
            agents_itter = random.sample(agents.sprites(), len(agents))
        else:
            agents_itter = agents.sprites()

        for robot in agents_itter:
            robot.updateNextTS(cfg, home_rect, food_rect, tunnel_rect, agents)
            #if it's asyncronous updates then update the agent immediately in the main loop
            if (cfg.UPDATETYPE == cfg.UPDATE_TYPES['async']) or (cfg.UPDATETYPE == cfg.UPDATE_TYPES['async_reverse']) or (cfg.UPDATETYPE == cfg.UPDATE_TYPES['async_random']):
                food_collected_b = robot.advanceTime(cfg, ticks, tunnel_rect)
                if food_collected_b:
                    food_collected_in_tick_b = True

        #if it's syncronous updates then update all the agents outside the main loop
        if cfg.UPDATETYPE == cfg.UPDATE_TYPES['sync']:
            for robot in agents.sprites():
                food_collected_b = robot.advanceTime(cfg, ticks, tunnel_rect)
                if food_collected_b:
                    food_collected_in_tick_b = True

        #if simulation is being visualised     
        if cfg.DRAWSCREEN:
            #Blank the screen buffer!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            screen.fill(cfg.WHITE)

            #draw the screen
            agents.draw(screen)
            obstacles.draw(screen)
            pygame.draw.rect(screen,cfg.GREEN,home_rect,2)
            pygame.draw.rect(screen,cfg.BLUE,food_rect,2)

            #flip the buffers to show the updated screen
            pygame.display.flip()

        #sets the update speed of the simulation only when it is being visualised.  A lower number is slower.
        # if not visualised then the simulation runs as fast as possible
        if cfg.DRAWSCREEN:
            clock.tick(cfg.TICK_RATE)

        #keep track of when last food was collected
        if food_collected_in_tick_b:
            food_last_collected_on_tick = ticks

        #update passage of time
        ticks +=cfg.DT
        
        #break out of the simulation loop early if a deadlock forms which cannot be recovered within a time limit
        if (ticks-food_last_collected_on_tick)>5000:
            stuck_b = True
            print(f"Agents became stuck on tick {ticks}")
    #end while

    #Do post simulation tasks
    from datetime import datetime
    data_all = []
    session_id = datetime.now().strftime("%Y%m%dT%H%M%S")
    #print("--------------------")
    print(f"session ID: {session_id}")
    if stuck_b:
        print(f"Agents became stuck on tick {ticks}")
    for robot in agents.sprites():
        #print("--------------------")
        #robot.printLog(cfg)
        #print("--------------------")
        header, data = robot.log.getLog(cfg)
        data_all.append(data)
    return session_id, header, data_all, ticks
#end main


if __name__=='__main__':
    main()