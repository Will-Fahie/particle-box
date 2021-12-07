"""
CONTROLS
left click: Add a particle
(hold) left click: Add many particles
RETURN: Toggle gravity
lshift + return: Toggle circular motion
BACKSPACE: Toggle particle collisions
UP ARROW: Increment new particle size
DOWN ARROW: Decrement new particle size
LEFT ARROW: Decrease number of particles per click
RIGHT ARROW: Increase number of particles per click
LEFT SQUARE BRACKET: Decrease gravitational acceleration
RIGHT SQUARE BRACKET: Increase gravitational acceleration
lshift + LEFT SQUARE BRACKET: Decrease centripetal acceleration
lshift + RIGHT SQUARE BRACKET: Increase centripetal acceleration
z: Slow down time
x: Speed up time
p: Add particle
b: Add box
lshift + b: Add box with hole in
s: Add square
r: Add horizontal rectangle
lshift + r: Add vertical rectangle
ESCAPE: Delete everything
1: Simulation 1
2: Simulation 2
3: Simulation 3
4: Simulation 4
5: Simulation 5
6: Simulation 6
7: Simulation 7
8: Simulation 8
9: Simulation 9
"""

import pygame
import numpy as np
import random
import time


COEFFICIENT_RESTITUTION = 1

# colours
BACKGROUND_COLOUR = (255, 255, 255)
PARTICLE_COLOUR = (50, 85, 140)
WALL_COLOUR = (0, 0, 0)
SHAPE_COLOUR = (100, 100, 100)
TEXT_COLOUR = (0, 0, 0)

# dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 600
PARTICLE_WIDTH = 1
SHAPE_OUTLINE = 1
MINI_BOX_WIDTH = 250
MINI_BOX_HEIGHT = 250
MINI_BOX_OUTLINE = 5
MINI_BOX_WIDTH = 300
MINI_BOX_HEIGHT = 300
SQUARE_WIDTH = 100
SQUARE_HEIGHT = 100
RECTANGLE1_WIDTH = 200
RECTANGLE1_HEIGHT = 25
RECTANGLE2_WIDTH = 25
RECTANGLE2_HEIGHT = 200

# box shape
BOX_WIDTH = 1000
BOX_HEIGHT = 500
BOX_TOP = 50
BOX_BOTTOM = BOX_TOP + BOX_HEIGHT
BOX_LEFT = 100
BOX_RIGHT = BOX_LEFT + BOX_WIDTH
BOX_WALL_WIDTH = 5

G_SCALE = 0.005


class Box:
    def __init__(self, width, height):
        pygame.init()
        pygame.font.init()
        self.text_font = pygame.font.Font("./arial.ttf", 20)
        self.drawing_text = self.text_font.render("Drawing: shapes", True, TEXT_COLOUR)
        self.number_of_particles = 0
        self.number_particles_text = self.text_font.render(f"{self.number_of_particles}", True, TEXT_COLOUR)
        self.running = True
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Particle Box!")
        self.particles = []
        self.left_wall = pygame.Rect(BOX_LEFT, BOX_TOP, BOX_WALL_WIDTH, BOX_HEIGHT)
        self.right_wall = pygame.Rect(BOX_RIGHT, BOX_TOP, BOX_WALL_WIDTH, BOX_HEIGHT + BOX_WALL_WIDTH)
        self.top_wall = pygame.Rect(BOX_LEFT, BOX_TOP, BOX_WIDTH, BOX_WALL_WIDTH)
        self.bottom_wall = pygame.Rect(BOX_LEFT, BOX_BOTTOM, BOX_WIDTH, BOX_WALL_WIDTH)
        self.shapes = []
        self.new_particle_size = 1
        self.gravity = False
        self.g_scale = 0
        self.collisions = True
        self.current_drawing = "particles"
        self.new_particles = 1
        self.mouse_down = False
        self.last_spawn_position = (0, 0)
        self.last_shape_position = (0, 0)
        self.boxes = []
        self.last_key_pressed_time = 0
        self.paused = True
        self.time_step = 1.0
        self.circular_motion = False
        self.centripetal_acceleration = 0

    def run(self):
        while self.running:
            self.clock.tick(240)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                key = pygame.key.get_pressed()
                

                if key[pygame.K_RETURN] and not key[pygame.K_LSHIFT]:
                    if self.gravity:
                        self.gravity = False
                    else:
                        self.gravity = True

                if key[pygame.K_RETURN] and key[pygame.K_LSHIFT]:
                    if self.circular_motion:
                        self.circular_motion = False
                    else:
                        self.circular_motion = True

                if key[pygame.K_BACKSPACE]:
                    if self.collisions:
                        self.collisions = False
                    else:
                        self.collisions = True

                if key[pygame.K_p]:
                    self.current_drawing = "particles"

                if key[pygame.K_b]:
                    self.current_drawing = "box"

                if key[pygame.K_s]:
                    self.current_drawing = "square"

                if key[pygame.K_r]:
                    self.current_drawing = "rectangle 1"

                if key[pygame.K_r] and key[pygame.K_LSHIFT]:
                    self.current_drawing = "rectangle 2"
                    
                if key[pygame.K_b] and key[pygame.K_LSHIFT]:
                    self.current_drawing = "box2"
                    
                if key[pygame.K_1]:
                    if time.monotonic() - self.last_key_pressed_time > 0.1:  # stops conflict issues
                        self.last_key_pressed_time = time.monotonic()
                        self.reset()
                        self.paused = True
                        for i in range(300):
                          self.add_particle()
                          
                if key[pygame.K_2]:
                    if time.monotonic() - self.last_key_pressed_time > 0.1:
                        self.last_key_pressed_time = time.monotonic()
                        self.reset()
                        self.paused = True
                        self.gravity = True
                        self.g_scale = 0.01
                        for i in range(10):
                            self.add_particle(Particle(self, 3, position=(BOX_LEFT + 100 + i * 75, 100)))
                            
                if key[pygame.K_3]:
                    if time.monotonic() - self.last_key_pressed_time > 0.1:
                        self.last_key_pressed_time = time.monotonic()
                        self.reset()
                        self.paused = True
                        self.add_mini_box(MiniBox(self, BOX_LEFT + 75, BOX_TOP + 75, BOX_WIDTH // 2 - 175, BOX_HEIGHT - 175))
                        for i in range(12):
                            for k in range(12):
                                self.add_particle(Particle(self, 1, position=(BOX_LEFT + 100 + i * 25, BOX_TOP + 100 + k * 25), vel_x=None, vel_y=None))
                                
                                
                if key[pygame.K_4]:
                    if time.monotonic() - self.last_key_pressed_time > 0.1:
                        self.last_key_pressed_time = time.monotonic()
                        self.reset()
                        self.paused = True
                        self.add_shape(Shape(self, (BOX_LEFT + BOX_WIDTH // 2, BOX_TOP + 2), 10, 200))
                        self.add_shape(Shape(self, (BOX_LEFT + BOX_WIDTH // 2, BOX_TOP + BOX_HEIGHT - 200), 10, 200))
                        for i in range(19):
                            for k in range(19):
                                self.add_particle(Particle(self, 1, position=(BOX_LEFT + 25 + i * 25, BOX_TOP + 27 + k * 25), vel_x=None, vel_y=None))
                              
                if key[pygame.K_5]:
                    if time.monotonic() - self.last_key_pressed_time > 0.1:
                        self.last_key_pressed_time = time.monotonic()
                        self.reset()
                        self.paused = True
                        self.collisions = False
                        self.gravity = True
                        self.g_scale = 0.01
                        for i in range(7500):
                            self.add_particle()
                            
                if key[pygame.K_6]:
                    if time.monotonic() - self.last_key_pressed_time > 0.1:
                        self.last_key_pressed_time = time.monotonic()
                        self.reset()
                        self.paused = True
                        self.add_particle(Particle(self, 3, (BOX_LEFT + BOX_WIDTH // 4, BOX_TOP + BOX_HEIGHT // 2), vel_x=-2, vel_y=0))
                        self.add_particle(Particle(self, 3, (BOX_LEFT + 3*(BOX_WIDTH // 4), BOX_TOP + BOX_HEIGHT // 2), vel_x=2, vel_y=0))
                        self.add_particle(Particle(self, 3, (BOX_LEFT + BOX_WIDTH // 2 + 6, BOX_TOP + BOX_HEIGHT // 2), vel_x=0, vel_y=0))
                        self.add_particle(Particle(self, 3, (BOX_LEFT + BOX_WIDTH // 2 + 6, BOX_TOP + 24), vel_x=0, vel_y=3))
                        self.add_particle(Particle(self, 3, (BOX_LEFT + BOX_WIDTH // 2 + 6, BOX_TOP + BOX_HEIGHT - 20), vel_x=0, vel_y=-3))
                
                if key[pygame.K_7]:
                    if time.monotonic() - self.last_key_pressed_time > 0.1:
                        self.last_key_pressed_time = time.monotonic()
                        self.reset()
                        self.paused = True
                        for i in range(14):
                            for k in range(19):
                                if k == 0:
                                    self.add_particle(Particle(self, 2, (BOX_LEFT + 50, BOX_TOP + (i+1) * 34), vel_x=-6, vel_y=0))
                                else:
                                    self.add_particle(Particle(self, 2, (BOX_LEFT + (k+1) * 50, BOX_TOP + (i+1) * 34), vel_x=0, vel_y=0))
                
                if key[pygame.K_8]:
                    if time.monotonic() - self.last_key_pressed_time > 0.1:
                        self.last_key_pressed_time = time.monotonic()
                        self.reset()
                        self.paused = True
                        self.gravity = True
                        self.g_scale = 0.0025
                        self.time_step = 0.75
                        for i in range(15):
                              self.add_particle(Particle(self, 2, (BOX_LEFT + 50, BOX_TOP + 10 + (i+1) * 30), vel_x=3, vel_y=None))
                        for i in range(15):
                              self.add_particle(Particle(self, 2, (BOX_LEFT + BOX_WIDTH - 50, BOX_TOP + 10 + (i+1) * 30), vel_x=-3, vel_y=None))

                if key[pygame.K_9]:
                    if time.monotonic() - self.last_key_pressed_time > 0.1:
                        self.last_key_pressed_time = time.monotonic()
                        self.reset()
                        self.paused = True
                        self.circular_motion = True
                        self.collisions = False
                        self.centripetal_acceleration = 0.0005

                        for i in range(500):
                            self.add_particle()
                        

                        

                if key[pygame.K_LEFT]:
                    if not self.new_particles == 1:
                        self.new_particles = self.new_particles // 2

                if key[pygame.K_RIGHT]:
                    if not self.new_particles == 64:
                        self.new_particles = self.new_particles * 2

                if key[pygame.K_UP]:
                    if self.new_particle_size < 5:
                        self.new_particle_size += 1
                        
                if key[pygame.K_DOWN]:
                    if self.new_particle_size > 1:
                        self.new_particle_size -= 1
                        
                if key[pygame.K_RIGHTBRACKET] and not key[pygame.K_LSHIFT]:
                    if time.monotonic() - self.last_key_pressed_time > 0.1:
                        self.last_key_pressed_time = time.monotonic()
                        if self.g_scale < 0.025:
                            self.g_scale = round(self.g_scale + 0.005, 3)
                  
                if key[pygame.K_LEFTBRACKET] and not key[pygame.K_LSHIFT]:
                    if time.monotonic() - self.last_key_pressed_time > 0.1:
                        self.last_key_pressed_time = time.monotonic()
                        if self.g_scale > -0.025:
                            self.g_scale = round(self.g_scale - 0.005, 3)

                if key[pygame.K_LEFTBRACKET] and key[pygame.K_LSHIFT]:
                    if time.monotonic() - self.last_key_pressed_time > 0.1:
                        self.last_key_pressed_time = time.monotonic()
                        if self.centripetal_acceleration > -0.0005:
                            self.centripetal_acceleration = round(self.centripetal_acceleration - 0.0001, 4)

                if key[pygame.K_RIGHTBRACKET] and key[pygame.K_LSHIFT]:
                    if time.monotonic() - self.last_key_pressed_time > 0.1:
                        self.last_key_pressed_time = time.monotonic()
                        if self.centripetal_acceleration < 0.0005:
                            self.centripetal_acceleration = round(self.centripetal_acceleration + 0.0001, 4)
                        
                if key[pygame.K_z]:
                  if time.monotonic() - self.last_key_pressed_time > 0.05:
                      self.last_key_pressed_time = time.monotonic()
                      if self.time_step > -2:
                          self.time_step = round(self.time_step - 0.1, 2)
                          
                if key[pygame.K_x]:
                  if time.monotonic() - self.last_key_pressed_time > 0.05:
                      self.last_key_pressed_time = time.monotonic()
                      if self.time_step < 2:
                          self.time_step = round(self.time_step + 0.1, 2)
                    
                if key[pygame.K_ESCAPE]:
                  self.reset()
                  
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_down = True  # clicks mouse

                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_down = False  # releases mouse
                    
                if key[pygame.K_SPACE]:
                  if time.monotonic() - self.last_key_pressed_time > 0.1:
                      self.last_key_pressed_time = time.monotonic()
                      if self.paused:
                          self.paused = False
                      else:
                          self.paused = True

                if self.mouse_down:
                    if self.current_drawing == "particles":
                        if self.new_particles == 1:
                            new_x, new_y = pygame.mouse.get_pos()
                            prev_x, prev_y = self.last_spawn_position
                            if abs(new_x - prev_x) > 15 or abs(new_y - prev_y) > 15:
                                self.add_particle(Particle(self, self.new_particle_size, (new_x, new_y)))
                                self.last_spawn_position = new_x, new_y
                        else:
                            for i in range(self.new_particles):
                                my_box.add_particle(Particle(self, self.new_particle_size))

                    elif self.current_drawing == "box":
                        pos_x, pos_y = pygame.mouse.get_pos()
                        self.add_mini_box(MiniBox(self, pos_x, pos_y))
                        
                    elif self.current_drawing == "box2":
                        pos_x, pos_y = pygame.mouse.get_pos()
                        self.add_mini_box_2(MiniBox2(self, pos_x, pos_y))

                    elif self.current_drawing == "square":
                        self.add_shape(Shape(self, pygame.mouse.get_pos(), SQUARE_WIDTH, SQUARE_HEIGHT))

                    elif self.current_drawing == "rectangle 1":
                        self.add_shape(Shape(self, pygame.mouse.get_pos(), RECTANGLE1_WIDTH, RECTANGLE1_HEIGHT))

                    elif self.current_drawing == "rectangle 2":
                        self.add_shape(Shape(self, pygame.mouse.get_pos(), RECTANGLE2_WIDTH, RECTANGLE2_HEIGHT))

            self.screen.fill(BACKGROUND_COLOUR)
            self.draw_walls()
            self.draw_shapes()
            self.draw_text()
            self.step()
            pygame.display.flip()

        pygame.quit()

    def draw_walls(self):
        pygame.draw.rect(self.screen, WALL_COLOUR, self.left_wall)
        pygame.draw.rect(self.screen, WALL_COLOUR, self.right_wall)
        pygame.draw.rect(self.screen, WALL_COLOUR, self.top_wall)
        pygame.draw.rect(self.screen, WALL_COLOUR, self.bottom_wall)

    def step(self):
        for particle in self.particles:
            if not self.paused:
                particle.move()
            rect = self.draw_particle(particle)
            particle.rect = rect
            particle.check_collide()
            
    def pause(self):
        pygame.time.delay(500)
            
    def reset(self):
        self.particles = []
        self.number_of_particles = 0
        self.shapes = []
        self.boxes = []
        self.gravity = False
        self.collisions = True
        self.time_step = 1.0
        self.g_scale = 0
        self.centripetal_acceleration = 0
        self.circular_motion = False

    def add_particle(self, particle=None):
        if not particle:
            particle = Particle(my_box, self.new_particle_size)

        position_found = False

        while not position_found:
            collided = False
            for shape in self.shapes:
                if particle.rect.colliderect(shape.collision_box):
                    collided = True
                    particle.set_random_position()

            if not collided:
                position_found = True

        self.particles.append(particle)
        self.number_of_particles += 1

    def add_shape(self, shape):
        collided = False
        for other_shape in self.shapes:
            if shape.collision_box.colliderect(other_shape.collision_box):
                collided = True

        if not collided:
            self.shapes.append(shape)

    def add_mini_box(self, mini_box):
        collided = False
        for shape in self.shapes:
            if mini_box.collision_box.colliderect(shape.collision_box):
                collided = True
        for other_box in self.boxes:
            if mini_box.collision_box.colliderect(other_box.collision_box):
                collided = True

        if not collided:
            self.shapes.append(mini_box.top_wall)
            self.shapes.append(mini_box.bottom_wall)
            self.shapes.append(mini_box.left_wall)
            self.shapes.append(mini_box.right_wall)
            self.boxes.append(mini_box)
            
    def add_mini_box_2(self, mini_box_2):
        collided = False
        for shape in self.shapes:
            if mini_box_2.collision_box.colliderect(shape.collision_box):
                collided = True
        for other_box in self.boxes:
            if mini_box_2.collision_box.colliderect(other_box.collision_box):
                collided = True
              
        if not collided:
            self.shapes.append(mini_box_2.top_wall)
            self.shapes.append(mini_box_2.bottom_wall)
            self.shapes.append(mini_box_2.left_wall_1)
            self.shapes.append(mini_box_2.left_wall_2)
            self.shapes.append(mini_box_2.right_wall)
            self.boxes.append(mini_box_2)

    def draw_particle(self, particle):
        rect = pygame.draw.circle(self.screen,
                                  PARTICLE_COLOUR,
                                  (particle.pos_x, particle.pos_y),
                                  particle.radius,
                                  PARTICLE_WIDTH)
        return rect

    def draw_shapes(self):
        for shape in self.shapes:
            pygame.draw.rect(self.screen, SHAPE_COLOUR, shape.top_wall)
            pygame.draw.rect(self.screen, SHAPE_COLOUR, shape.bottom_wall)
            pygame.draw.rect(self.screen, SHAPE_COLOUR, shape.left_wall)
            pygame.draw.rect(self.screen, SHAPE_COLOUR, shape.right_wall)
            pygame.draw.rect(self.screen, SHAPE_COLOUR, shape.collision_box)  # shows where the shape will be added

        left, top = pygame.mouse.get_pos()
        if self.current_drawing == "box":
            left, top = pygame.mouse.get_pos()
            virtual_box = MiniBox(self, left, top)
            pygame.draw.rect(self.screen, SHAPE_COLOUR, virtual_box.top_wall.collision_box)
            pygame.draw.rect(self.screen, SHAPE_COLOUR, virtual_box.bottom_wall.collision_box)
            pygame.draw.rect(self.screen, SHAPE_COLOUR, virtual_box.left_wall.collision_box)
            pygame.draw.rect(self.screen, SHAPE_COLOUR, virtual_box.right_wall.collision_box)
            
        if self.current_drawing == "box2":
            left, top = pygame.mouse.get_pos()
            virtual_box = MiniBox2(self, left, top)
            pygame.draw.rect(self.screen, SHAPE_COLOUR, virtual_box.top_wall.collision_box)
            pygame.draw.rect(self.screen, SHAPE_COLOUR, virtual_box.bottom_wall.collision_box)
            pygame.draw.rect(self.screen, SHAPE_COLOUR, virtual_box.left_wall_1.collision_box)
            pygame.draw.rect(self.screen, SHAPE_COLOUR, virtual_box.left_wall_2.collision_box)
            pygame.draw.rect(self.screen, SHAPE_COLOUR, virtual_box.right_wall.collision_box)

        if self.current_drawing == "square":
            pygame.draw.rect(self.screen, SHAPE_COLOUR,
                             pygame.Rect(left, top, SQUARE_WIDTH + SHAPE_OUTLINE, SQUARE_HEIGHT + SHAPE_OUTLINE))

        if self.current_drawing == "rectangle 1":
            pygame.draw.rect(self.screen, SHAPE_COLOUR,
                             pygame.Rect(left, top, RECTANGLE1_WIDTH + SHAPE_OUTLINE, RECTANGLE1_HEIGHT + SHAPE_OUTLINE))

        if self.current_drawing == "rectangle 2":
            pygame.draw.rect(self.screen, SHAPE_COLOUR,
                             pygame.Rect(left, top, RECTANGLE2_WIDTH + SHAPE_OUTLINE, RECTANGLE2_HEIGHT + SHAPE_OUTLINE))

    def draw_text(self):
        self.screen.blit(self.text_font.render(f"Particles: {self.number_of_particles}", True, TEXT_COLOUR),
                         (50, 20))
        self.screen.blit(self.text_font.render(f"|   Gravity: {self.gravity}   |", True, TEXT_COLOUR),
                         (200, 20))
        self.screen.blit(self.text_font.render(f"Circular motion: {self.circular_motion}    |", True, TEXT_COLOUR),
                         (390, 20))
        self.screen.blit(self.text_font.render(f"Collisions: {self.collisions}    |", True, TEXT_COLOUR),
                         (630, 20))
        self.screen.blit(self.text_font.render(f"Paused: {self.paused}    |", True, TEXT_COLOUR),
                         (820, 20))
        self.screen.blit(self.text_font.render(f"Drawing: {self.current_drawing}", True, TEXT_COLOUR),
                         (985, 20))
        self.screen.blit(self.text_font.render(f"New particle size: {self.new_particle_size}", True, TEXT_COLOUR),
                         (100, WINDOW_HEIGHT - 40))
        self.screen.blit(self.text_font.render(f"New particles: {self.new_particles}", True, TEXT_COLOUR),
                         (300, WINDOW_HEIGHT - 40))
        self.screen.blit(self.text_font.render(f"Time step: {self.time_step}", True, TEXT_COLOUR),
                         (500, WINDOW_HEIGHT - 40))
        self.screen.blit(self.text_font.render(f"g scale: {self.g_scale}", True, TEXT_COLOUR),
                         (700, WINDOW_HEIGHT - 40))
        self.screen.blit(self.text_font.render(f"Centripetal acceleration: {self.centripetal_acceleration}", True, TEXT_COLOUR),
                         (850, WINDOW_HEIGHT - 40))


class Shape:
    def __init__(self, box, position, width, height):
        self.box = box
        self.left = position[0]
        self.top = position[1]
        self.width = width
        self.height = height
        self.outline_width = SHAPE_OUTLINE
        self.top_wall = pygame.Rect(self.left, self.top, self.width, self.outline_width)
        self.bottom_wall = pygame.Rect(self.left, self.top + self.height, self.width, self.outline_width)
        self.left_wall = pygame.Rect(self.left, self.top, self.outline_width, self.height)
        self.right_wall = pygame.Rect(self.left + self.width, self.top, self.outline_width, self.height + self.outline_width)
        self.collision_box = pygame.Rect(self.left, self.top, self.width + self.outline_width, self.height + self.outline_width)


class MiniBox:
    def __init__(self, box, left, top, width=None, height=None):
        self.box = box
        self.left = left
        self.top = top
        if width is None:
            self.width = MINI_BOX_WIDTH
        else:
            self.width = width
        if height is None:
            self.height = MINI_BOX_HEIGHT
        else:
            self.height = height
        self.top_wall = Shape(self.box, (left, top), self.width, MINI_BOX_OUTLINE)
        self.bottom_wall = Shape(self.box, (left, top + self.height), self.width + MINI_BOX_OUTLINE , MINI_BOX_OUTLINE)
        self.left_wall = Shape(self.box, (left, top), MINI_BOX_OUTLINE, self.height)
        self.right_wall = Shape(self.box, (left + self.width, top), MINI_BOX_OUTLINE, self.height)
        self.collision_box = pygame.Rect(self.left, self.top, self.width, self.height)
        
        
class MiniBox2:
    def __init__(self, box, left, top, width=None, height=None):
        self.box = box
        self.left = left
        self.top = top
        if width is None:
            self.width = MINI_BOX_WIDTH
        else:
            self.width = width
        if height is None:
            self.height = MINI_BOX_HEIGHT
        else:
            self.height = height
        self.top_wall = Shape(self.box, (left, top), self.width, MINI_BOX_OUTLINE)
        self.bottom_wall = Shape(self.box, (left, top + self.height), self.width + MINI_BOX_OUTLINE , MINI_BOX_OUTLINE)
        self.left_wall_1 = Shape(self.box, (left, top), MINI_BOX_OUTLINE, self.height-200)
        self.left_wall_2 = Shape(self.box, (left, top + self.height-100), MINI_BOX_OUTLINE, self.height-200)
        self.right_wall = Shape(self.box, (left + self.width, top), MINI_BOX_OUTLINE, self.height)
        self.collision_box = pygame.Rect(self.left, self.top, self.width, self.height)


class Particle:
    def __init__(self, box, mass, position=None, vel_x=None, vel_y=None):
        self.box = box
        self.mass = mass
        self.radius = self.mass * 5
        if vel_x is None:
            self.vel_x = random.random() * random.randint(-2, 2)
        else:
            self.vel_x = vel_x
        if vel_y is None:
            self.vel_y = random.random() * random.randint(-2, 2)
        else:
            self.vel_y = vel_y
        if not position:
            self.pos_x = random.randint(BOX_LEFT + self.radius, BOX_RIGHT - self.radius)
            self.pos_y = random.randint(BOX_TOP + self.radius, BOX_BOTTOM - self.radius)
        else:
            self.pos_x, self.pos_y = position[0], position[1]
        self.rect = pygame.draw.circle(self.box.screen, PARTICLE_COLOUR, (self.pos_x, self.pos_y), self.radius)
        self.previous_collision = None

    def move(self):
        if self.box.circular_motion:
            self.vel_x += (BOX_LEFT + BOX_WIDTH // 2 - self.pos_x)* self.box.centripetal_acceleration
            self.vel_y += (BOX_TOP + BOX_HEIGHT // 2 - self.pos_y) * self.box.centripetal_acceleration
        if self.box.gravity:
            self.vel_y += self.box.g_scale * 9.81 * self.box.time_step

        self.pos_x += self.vel_x * self.box.time_step
        self.pos_y += self.vel_y * self.box.time_step

    def set_random_position(self):
        self.pos_x = random.randint(BOX_LEFT + self.radius, BOX_RIGHT - self.radius)
        self.pos_y = random.randint(BOX_TOP + self.radius, BOX_BOTTOM - self.radius)
        self.rect = pygame.draw.circle(self.box.screen, PARTICLE_COLOUR, (self.pos_x, self.pos_y), self.radius)

    def check_collide(self):
        # collision with particles and shapes
        if self.box.collisions:
            for particle in self.box.particles:
                if self.rect.colliderect(particle.rect) and particle != self:
                    if not(self.previous_collision == particle and particle.previous_collision == self):
                        self.bounce(particle)
                        self.previous_collision = particle
                        particle.previous_collision = self

            for shape in self.box.shapes:
                if self.rect.colliderect(shape.top_wall):
                    self.pos_y -= 2
                    self.vel_y = -self.vel_y * COEFFICIENT_RESTITUTION
                    self.previous_collision = shape

                elif self.rect.colliderect(shape.bottom_wall):
                    self.pos_y += 2
                    self.vel_y = -self.vel_y * COEFFICIENT_RESTITUTION
                    self.previous_collision = shape

                elif self.rect.colliderect(shape.left_wall):
                    self.pos_x -= 2
                    self.vel_x = -self.vel_x * COEFFICIENT_RESTITUTION
                    self.previous_collision = shape

                elif self.rect.colliderect(shape.right_wall):
                    self.pos_x += 2
                    self.vel_x = -self.vel_x * COEFFICIENT_RESTITUTION
                    self.previous_collision = shape

      # collision with walls
        if self.rect.colliderect(self.box.left_wall):
            self.pos_x += 2  # moves particle away from wall to avoid clipping issues
            self.vel_x = -self.vel_x * COEFFICIENT_RESTITUTION
            self.previous_collision = self.box.left_wall

        elif self.rect.colliderect(self.box.right_wall):
            self.pos_x -= 2
            self.vel_x = -self.vel_x * COEFFICIENT_RESTITUTION
            self.previous_collision = self.box.right_wall

        elif self.rect.colliderect(self.box.top_wall):
            self.pos_y += 2
            self.vel_y = -self.vel_y * COEFFICIENT_RESTITUTION
            self.previous_collision = self.box.top_wall

        elif self.rect.colliderect(self.box.bottom_wall):
            self.pos_y -= 2
            self.vel_y = -self.vel_y * COEFFICIENT_RESTITUTION
            self.previous_collision = self.box.bottom_wall

    def calc_momentum_components(self):
        return self.vel_x * self.mass, self.vel_y * self.mass

    def bounce(self, particle):
        mass_1, mass_2 = self.mass, particle.mass

        # initial velocities
        u_x_1, u_x_2 = self.vel_x, particle.vel_x
        u_y_1, u_y_2 = self.vel_y, particle.vel_y

        # momenta
        momentum_1_x, momentum_1_y = self.calc_momentum_components()
        momentum_2_x, momentum_2_y = particle.calc_momentum_components()

        # setting up and solving simultaneous equations
        coefficients = [[mass_1, mass_2], [-1, 1]]
        results_x = [momentum_1_x + momentum_2_x, COEFFICIENT_RESTITUTION * (u_x_1 - u_x_2)]
        results_y = [momentum_1_y + momentum_2_y, COEFFICIENT_RESTITUTION * (u_y_1 - u_y_2)]

        self.vel_x, particle.vel_x = np.linalg.solve(coefficients, results_x)
        self.vel_y, particle.vel_y = np.linalg.solve(coefficients, results_y)


if __name__ == "__main__":
    my_box = Box(WINDOW_WIDTH, WINDOW_HEIGHT)
    my_box.run()
  
