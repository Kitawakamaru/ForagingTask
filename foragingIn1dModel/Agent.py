import numpy as np
import sys, pygame

#Agent is a super class for Robot
class Agent(pygame.sprite.Sprite):
    # Agents are a subclass of Pygame sprites.
    def __init__(self, position, type) -> None:
        #intialise the agent as a pygame sprite
        pygame.sprite.Sprite.__init__(self)

        #declare the physical properties (need to be declared before the sprite image)
        self.m_sensor_range = 10
        self.m_position = np.asarray(position)

        #declare the locical properties
        self.m_id = 0
        self.m_type = type

        #create a token sprint image
        self.m_sprite_position = pygame.math.Vector2((position[0], position[1] ))
        img = pygame.Surface((10,10))
        img = pygame.transform.smoothscale(img, (10,10))
        GREEN = 0, 255, 0
        img.fill(GREEN)
        self.setImage(img)

        #declare containers for cached information
        self.m_adj_free_squares = []
        self.m_adj_free_squares_is_current_b = False
        return
    #end function


    def loadImage(self,imageName, sq_size):
        '''loads and scales an image for the agent'''
        image = pygame.image.load(imageName)
        image = pygame.transform.smoothscale(image, (sq_size,sq_size))
        return image
    #end function


    def setImage(self, image):
        '''overlays the image at the agent's current position'''
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.m_sprite_position
        return
    #end function


    def setPosition(self, new_position):
        '''set a new position for the agent in the world'''
        self.m_position = np.asarray(new_position)
        return self.m_position
    #end function


    def setSpritePosition(self, new_position):
        '''set a new position for the sprite
        the sprite is the visual representation of the agent'''
        #ensure new_position is a 1D vector
        new_position = np.squeeze(new_position)
        self.m_sprite_position = pygame.math.Vector2((new_position[0],new_position[1]))
        self.rect.center = round(self.m_sprite_position.x), round(self.m_sprite_position.y)
        return self.m_sprite_position
    #end function


    def updateSprite(self, scale_factor):
        ''' simple function which moves the agents image to align with its position in the screen coordinate frame '''
        pos_in_screen_coords = self.m_position * scale_factor
        self.setSpritePosition(pos_in_screen_coords)
        return
    #end function

    def angleBetweenVectors(self, u,v):
        '''Calculates the oblique angle (0..pi)  between two vectors.
        if a list of vectors is provided then it must be N x dimensions e.g. N x 2 for 2D vectors '''

        #ensure both u and v are 2 axis and in the format N x 2
        u = np.atleast_2d(u)
        v = np.atleast_2d(v)
        
        if u.shape[0]==1 or v.shape[0]==1:
            dotuv = np.sum(u * v, axis=1)
        else:
            dotuv = np.dot(u,v)
        
        #normalise the result
        dotuv = dotuv/(np.linalg.norm(u) * np.linalg.norm(v))

        #need to ensure that numerical rounding doesn't cause the result to go outside the range -1 to +1
        cos_theta = np.clip(dotuv, -1,+1)

        #take the arc and return
        theta = np.real(np.arccos(cos_theta))

        return theta
    #end funciton