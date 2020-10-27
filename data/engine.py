from copy import deepcopy

import math
import noise
import os
import pygame
import random

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
light_blue = (0, 255, 255)
yellow = (255, 255, 0)
purple = (255, 0, 255)
global anim_path
anim_path = ""

font_dat = {'A':[3],'B':[3],'C':[3],'D':[3],'E':[3],'F':[3],'G':[3],'H':[3],'I':[3],'J':[3],'K':[3],'L':[3],'M':[5],'N':[3],'O':[3],'P':[3],'Q':[3],'R':[3],'S':[3],'T':[3],'U':[3],'V':[3],'W':[5],'X':[3],'Y':[3],'Z':[3],
          'a':[3],'b':[3],'c':[3],'d':[3],'e':[3],'f':[3],'g':[3],'h':[3],'i':[1],'j':[2],'k':[3],'l':[3],'m':[5],'n':[3],'o':[3],'p':[3],'q':[3],'r':[2],'s':[3],'t':[3],'u':[3],'v':[3],'w':[5],'x':[3],'y':[3],'z':[3],
          '.':[1],'-':[3],',':[2],':':[1],'+':[3],'\'':[1],'!':[1],'?':[3],
          '0':[3],'1':[3],'2':[3],'3':[3],'4':[3],'5':[3],'6':[3],'7':[3],'8':[3],'9':[3],
          '(':[2],')':[2],'/':[3],'_':[5],'=':[3],'\\':[3],'[':[2],']':[2],'*':[3],'"':[3],'<':[3],'>':[3],';':[1]}

global e_colorkey
e_colorkey = white

pygame.init()

Monitor = pygame.display.Info()

class Spritesheet(object):
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert()

    def image_at(self, rectangle, colorkey = None):
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey != None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(white)
        return image

    def images_at(self, rects, colorkey = None):
        return [self.image_at(rect, colorkey) for rect in rects]

    def width(self):
        return self.sheet.get_width()

def set_global_colorkey(colorkey):
    global e_colorkey
    e_colorkey = colorkey

# physics core

# 2d collisions test
def collision_test(object_1,object_list):
    collision_list = []
    for obj in object_list:
        if obj.colliderect(object_1):
            collision_list.append(obj)
    return collision_list

# 2d physics object
class physics_obj(object):
   
    def __init__(self,x,y,x_size,y_size):
        self.width = x_size
        self.height = y_size
        self.rect = pygame.Rect(x,y,self.width,self.height)
        self.x = x
        self.y = y
       
    def move(self,movement,platforms,ramps=[]):
        self.x += movement[0]
        self.rect.x = int(self.x)
        block_hit_list = collision_test(self.rect,platforms)
        collision_types = {'top':False,'bottom':False,'right':False,'left':False,'slant_bottom':False,'data':[]}
        # added collision data to "collision_types". ignore the poorly chosen variable name
        for block in block_hit_list:
            markers = [False,False,False,False]
            if movement[0] > 0:
                self.rect.right = block.left
                collision_types['right'] = True
                markers[0] = True
            elif movement[0] < 0:
                self.rect.left = block.right
                collision_types['left'] = True
                markers[1] = True
            collision_types['data'].append([block,markers])
            self.x = self.rect.x
        self.y += movement[1]
        self.rect.y = int(self.y)
        block_hit_list = collision_test(self.rect,platforms)
        for block in block_hit_list:
            markers = [False,False,False,False]
            if movement[1] > 0:
                self.rect.bottom = block.top
                collision_types['bottom'] = True
                markers[2] = True
            elif movement[1] < 0:
                self.rect.top = block.bottom
                collision_types['top'] = True
                markers[3] = True
            collision_types['data'].append([block,markers])
            self.change_y = 0
            self.y = self.rect.y
        return collision_types

# entity stuff

def flip(img,boolean=True, boolean_2=False):
    return pygame.transform.flip(img,boolean,boolean_2)
 
def blit_center(surf: object, surf2: object, pos: object, scaling) -> object:
    x = int(surf2.get_width()/2)
    y = int(surf2.get_height()/2)
    surf.blit(pygame.transform.scale(surf2, (surf2.get_size()[0] * scaling, surf2.get_size()[1] * scaling)),(pos[0]-x,pos[1]-y))
 
class entity(object):
    def __init__(self,x,y,size_x,size_y,e_type, colorkey = e_colorkey): # x, y, size_x, size_y, type, colorkey
        self.scale = 1
        self.x = x
        self.y = y
        self.size_x = size_x
        self.size_y = size_y
        self.colorkey = colorkey
        self.obj = physics_obj(x, y, size_x * self.scale, size_y * self.scale)
        self.image_path = anim_path + e_type + "/idle.png"
        self.sheet = Spritesheet(self.image_path)
        self.image = self.sheet.image_at((32, 0, self.size_x, self.size_y), self.colorkey)
        self.flip = False
        self.offset = [0,0]
        self.rotation = 0
        self.type = e_type # used to determine animation set among other things
        self.action = "idle"
        self.alpha = None
        self.current_frame = 0
        self.totalframes = self.sheet.width() / self.size_x
        self.countframes = 0
        self.animations = {}
        for anim in anim_database:
            if self.type in anim:
                self.animations[anim.split("/")[-1]] = anim_database[anim]
        self.start()
        self.next_step = int(self.animations[self.action][0][self.current_frame])
        self.set_action('idle')  # overall action for the entity

    def scale_size(self, scaling):
        self.scale = scaling
        self.obj = physics_obj(self.x, self.y, self.size_x * self.scale, self.size_y * self.scale)

    def set_pos(self,x,y):
        self.x = x
        self.y = y
        self.obj.x = x
        self.obj.y = y
        self.obj.rect.x = x
        self.obj.rect.y = y
 
    def move(self,momentum,platforms,ramps=[]):
        collisions = self.obj.move(momentum,platforms,ramps)
        self.x = self.obj.x
        self.y = self.obj.y
        return collisions
 
    def rect(self):
        return pygame.Rect(self.x,self.y,self.size_x,self.size_y)
 
    def set_flip(self,boolean):
        self.flip = boolean
 
    def set_action(self,action_id):
        if self.action == action_id:
            pass
        else:
            self.action = action_id
            self.image_path = anim_path + self.type + "/" + action_id + ".png"
            self.sheet = Spritesheet(self.image_path)
            self.image = self.sheet.image_at((0, 0, self.size_x, self.size_y), self.colorkey)
            self.totalframes = self.sheet.width() / self.size_x
            self.running = True
            self.current_frame = 0
            self.next_step = int(self.animations[self.action][0][self.current_frame])
            self.countframes = 0

    def get_entity_angle(entity_2):
        x1 = self.x+int(self.size_x/2)
        y1 = self.y+int(self.size_y/2)
        x2 = entity_2.x+int(entity_2.size_x/2)
        y2 = entity_2.y+int(entity_2.size_y/2)
        angle = math.atan((y2-y1)/(x2-x1))
        if x2 < x1:
            angle += math.pi
        return angle

    def get_center(self):
        x = self.x+int(self.size_x/2)
        y = self.y+int(self.size_y/2)
        return [x,y]

    def get_pos(self):
        return [self.x, self.y]
 
    def set_image(self,image):
        self.image = image

    def start(self):
        self.running = True

    def stop(self):
        self.running = False
 
    def handle(self):
        self.action_timer += 1
        self.change_frame(1)
 
    def change_frame(self, current):
        if self.running:
            self.next_step = int(self.animations[self.action][0][self.current_frame])
            self.countframes += current
            if self.countframes == self.next_step:
                self.countframes = 0
                self.current_frame += 1
            if self.current_frame == self.totalframes:
                self.current_frame = 0
                if self.animations[self.action][-1] != "loop":
                    self.running = False
            self.image = self.sheet.image_at((self.current_frame * self.size_x, 0, self.size_x, self.size_y), self.colorkey)

    def display(self,surface):
        image_to_render = self.image
        if image_to_render != None:
            center_x = image_to_render.get_width()/2
            center_y = image_to_render.get_height()/2
            image_to_render = pygame.transform.rotate(image_to_render,self.rotation)
            if self.alpha != None:
                image_to_render.set_alpha(self.alpha)
            blit_center(surface,flip(image_to_render, self.flip),(int(self.x)+self.offset[0]+center_x,int(self.y)+self.offset[1]+center_y), self.scale)

# particles
global anim_database
anim_database = {}

def load_animations(path):
    global anim_path, anim_database
    anim_path = path
    with open(anim_path + "/animations_info.txt", "r") as f:
        data = f.read()
    data = data.split("\n")
    for anim in data:
        relative_to, duration, tags = anim.split(" ")
        anim_database[relative_to] = [duration.split(";"), tags]

global particle_path

def enable_particles():
    global particle_path
    particle_path = anim_path + "/particles/"

class Particle:
    def __init__(self, X, Y, motion, width, height, type, step = 4, colorkey = e_colorkey, enable_physics = False, physics = [0, []]):
        self.x = X
        self.y = Y
        self.w = width
        self.h = height
        self.type = type
        self.colorkey = colorkey
        self.sheet = Spritesheet(particle_path + self.type + ".png")
        self.current_frame = 0
        self.img = self.sheet.image_at((self.current_frame, self.current_frame, self.w, self.h), self.colorkey)
        self.totalframes = self.sheet.width() / self.w
        self.step = step
        self.countframes = 0
        self.running = True
        self.motion = list(motion)
        self.delta_motion = [abs(self.motion[0] / self.totalframes), abs(self.motion[1] / self.totalframes)]
        self.g = physics[0]
        self.colliding = physics[1]
        self.physics = enable_physics
        self.obj = physics_obj(self.x, self.y, self.w, self.h)

    def display(self, display, scale = 1):
        display.blit(pygame.transform.scale(self.img, (self.w * scale, self.h * scale)), (self.x, self.y))

    def is_alive(self):
        return self.running

    def update(self):
        if self.running:
            if self.motion[0] > 0:
                self.motion[0] -= self.delta_motion[0]
                if self.motion[0] < 1:
                    self.motion[0] = 0
            elif self.motion[0] < 0:
                self.motion[0] += self.delta_motion[0]
                if self.motion[0] > -1:
                    self.motion[0] = 0
            if self.motion[1] > 0:
                self.motion[1] -= self.delta_motion[1]
                if self.motion[1] < 1:
                    self.motion[1] = 0
            elif self.motion[1] < 0:
                self.motion[1] += self.delta_motion[1]
                if self.motion[1] > -1:
                    self.motion[1] = 0
            if self.physics:
                self.motion[1] += self.g
                if self.motion[1] > self.g:
                    self.motion[1] -= 2
                collisions = self.obj.move(self.motion, self.colliding)
                if collisions["top"] or collisions["bottom"]:
                    self.motion[1] = 0
                if collisions["left"] or collisions["right"]:
                    self.motion[0] = 0

                self.x = self.obj.x
                self.y = self.obj.y
            else:
                self.x += self.motion[0]
                self.y += self.motion[1]

            self.countframes += 1
            if self.countframes >= self.step:
                self.countframes = 0
                self.current_frame += 1
            if self.current_frame < self.totalframes:
                self.img = self.sheet.image_at((self.current_frame * self.w, 0, self.w, self.h), self.colorkey)
            else:
                self.running = False

    def play(self, display):
        self.update()
        self.display(display)
        
# other useful functions

def swap_color(img,old_c,new_c):
    global e_colorkey
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img,(0,0))
    surf.set_colorkey(e_colorkey)
    return surf

def generate_flat_chunk(x,y, CHUNK_SIZE):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0 # nothing
            if target_y > 10:
                tile_type = 2 # dirt
            elif target_y == 10:
                tile_type = 1 # grass
            elif target_y == 9:
                if random.randint(1,5) == 1:
                    tile_type = 3 # plant
            if tile_type != 0:
                chunk_data.append([[target_x,target_y],tile_type])
    return chunk_data

def generate_chunk(x,y, CHUNK_SIZE, offset = 0.1, multiplier = 5):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0 # nothing
            off = int(noise.pnoise1(target_x * offset, repeat=9999999) * multiplier)
            if target_y > 10 - off:
                tile_type = 4 # stone
            if target_y <= 10 - off + round(random.random()) and target_y > 8 - off:
                tile_type = 2 # dirt
            elif target_y == 8 - off:
                tile_type = 1 # grass
            elif target_y == 8 - off - 1:
                if random.randint(1,5) == 1:
                    tile_type = 3 # plant
            if tile_type != 0:
                chunk_data.append([[target_x,target_y],tile_type])
    return chunk_data

def block_at(pos, CHUNK_SIZE, off, chunk):
    posx = int(int((pos[0] + off[0]) / 2) / CHUNK_SIZE)
    posy = int(int((pos[1] + off[1]) / 2) / CHUNK_SIZE)
    for a in chunk:
        if a[0] == [posx, posy]:
            return chunk.index(a)

def show_text(Text,X,Y,wl,Font,surface,scaling=1,overflow='normal', Spacing=1):
    Text += ' '
    OriginalX = X
    OriginalY = Y
    X = 0
    Y = 0
    CurrentWord = ''
    WidthLimit = wl / scaling + OriginalX
    if overflow == 'normal':
        for char in Text:
            if char not in [' ','\n']:
                try:
                    Image = Font[str(char)][1]
                    CurrentWord += str(char)
                except KeyError:
                    pass
            else:
                WordTotal = 0
                for char2 in CurrentWord:
                    WordTotal += Font[char2][0]
                    WordTotal += Spacing
                if WordTotal+X+OriginalX > WidthLimit:
                    X = 0
                    Y += Font['Height']
                for char2 in CurrentWord:
                    Image = Font[str(char2)][1]
                    surface.blit(pygame.transform.scale(Image,(Image.get_width()*scaling,Image.get_height()*scaling)),(X * scaling + OriginalX,Y * scaling + OriginalY))
                    X += Font[char2][0]
                    X += Spacing
                if char == ' ':
                    X += Font['A'][0]
                    X += Spacing
                else:
                    X = 0
                    Y += Font['Height']
                CurrentWord = ''
            if X+OriginalX > WidthLimit:
                X = 0
                Y += Font['Height']
        return X,Y
    if overflow == 'cut all':
        for char in Text:
            if char not in [' ','\n']:
                try:
                    Image = Font[str(char)][1]
                    surface.fill(green)
                    surface.blit(pygame.transform.scale(Image,(Image.get_width()*scaling,Image.get_height()*scaling)),(X*scaling,Y*scaling))
                    X += Font[str(char)][0]
                    X += Spacing
                except KeyError:
                    pass
            else:
                if char == ' ':
                    X += Font['A'][0]
                    X += Spacing
                if char == '\n':
                    X = 0
                    Y += Font['Height']
                CurrentWord = ''
            if X+OriginalX > WidthLimit:
                X = 0
                Y += Font['Height']
        return X,Y

def generate_font(FontImage,FontSpacingMain,TileSize,TileSizeY,color):
    FontSpacing = deepcopy(FontSpacingMain)
    FontOrder = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','.','-',',',':','+','\'','!','?','0','1','2','3','4','5','6','7','8','9','(',')','/','_','=','\\','[',']','*','"','<','>',';']
    FontImage = pygame.image.load(FontImage).convert()
    NewSurf = pygame.Surface((FontImage.get_width(),FontImage.get_height())).convert()
    NewSurf.fill(color)
    FontImage.set_colorkey((0,0,0))
    NewSurf.blit(FontImage,(0,0))
    FontImage = NewSurf.copy()
    FontImage.set_colorkey((255,255,255))
    num = 0
    for char in FontOrder:
        FontImage.set_clip(pygame.Rect(((TileSize+1)*num),0,TileSize,TileSizeY))
        CharacterImage = FontImage.subsurface(FontImage.get_clip())
        FontSpacing[char].append(CharacterImage)
        num += 1
    FontSpacing['Height'] = TileSizeY
    return FontSpacing
