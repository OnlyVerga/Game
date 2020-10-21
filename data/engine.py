import pygame, math, os, random, noise
from copy import deepcopy

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

class Spritesheet(object):
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert()

    def image_at(self, rectangle, colorkey = None):
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey = None):
        return [self.image_at(rect, colorkey) for rect in rects]

    def width(self):
        return self.sheet.get_width()



global e_colorkey
e_colorkey = white

pygame.init()

Monitor = pygame.display.Info()

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

class cuboid(object):
    
    def __init__(self,x,y,z,x_size,y_size,z_size):
        self.x = x
        self.y = y
        self.z = z
        self.x_size = x_size
        self.y_size = y_size
        self.z_size = z_size
        
    def set_pos(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
        
    def collidecuboid(self,cuboid_2):
        cuboid_1_xy = pygame.Rect(self.x,self.y,self.x_size,self.y_size)
        cuboid_1_yz = pygame.Rect(self.y,self.z,self.y_size,self.z_size)
        cuboid_2_xy = pygame.Rect(cuboid_2.x,cuboid_2.y,cuboid_2.x_size,cuboid_2.y_size)
        cuboid_2_yz = pygame.Rect(cuboid_2.y,cuboid_2.z,cuboid_2.y_size,cuboid_2.z_size)
        if (cuboid_1_xy.colliderect(cuboid_2_xy)) and (cuboid_1_yz.colliderect(cuboid_2_yz)):
            return True
        else:
            return False

# entity stuff

def simple_entity(x,y,e_type):
    return entity(x,y,1,1,e_type)

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
        self.action = ""
        self.set_action('idle') # overall action for the entity
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
                if self.animations[self.action][1] != "loop":
                    self.running = False
            self.image = self.sheet.image_at((self.current_frame * self.size_x, 0, self.size_x, self.size_y))

    def display(self,surface):
        image_to_render = self.image
        if image_to_render != None:
            center_x = image_to_render.get_width()/2
            center_y = image_to_render.get_height()/2
            image_to_render = pygame.transform.rotate(image_to_render,self.rotation)
            if self.alpha != None:
                image_to_render.set_alpha(self.alpha)
            blit_center(surface,image_to_render,(int(self.x)+self.offset[0]+center_x,int(self.y)+self.offset[1]+center_y), self.scale)

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

def particle_file_sort(l):
    l2 = []
    for obj in l:
        l2.append(int(obj[:-4]))
    l2.sort()
    l3 = []
    for obj in l2:
        l3.append(str(obj) + '.png')
    return l3

global particle_images
particle_images = {}

def load_particle_images(path):
    global particle_images, e_colorkey
    file_list = os.listdir(path)
    for folder in file_list:
        try:
            img_list = os.listdir(path + '/' + folder)
            img_list = particle_file_sort(img_list)
            images = []
            for img in img_list:
                images.append(pygame.image.load(path + '/' + folder + '/' + img).convert())
            for img in images:
                img.set_colorkey(e_colorkey)
            particle_images[folder] = images.copy()
        except:
            pass

class particle(object):

    def __init__(self,x,y,particle_type,motion,decay_rate,start_frame,custom_color=None):
        self.x = x
        self.y = y
        self.type = particle_type
        self.motion = motion
        self.decay_rate = decay_rate
        self.color = custom_color
        self.frame = start_frame

    def draw(self,surface,scroll):
        global particle_images
        if self.frame > len(particle_images[self.type])-1:
            self.frame = len(particle_images[self.type])-1
        if self.color == None:
            blit_center(surface,particle_images[self.type][int(self.frame)],(self.x-scroll[0],self.y-scroll[1]))
        else:
            blit_center(surface,swap_color(particle_images[self.type][int(self.frame)],(255,255,255),self.color),(self.x-scroll[0],self.y-scroll[1]))

    def update(self):
        self.frame += self.decay_rate
        running = True
        if self.frame > len(particle_images[self.type])-1:
            running = False
        self.x += self.motion[0]
        self.y += self.motion[1]
        return running
        
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

def show_text(Text,X,Y,WidthLimit,Font,surface,scaling=1,overflow='normal', Spacing=1):
    Text += ' '
    OriginalX = X
    OriginalY = Y
    X = 0
    Y = 0
    CurrentWord = ''
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
                if WordTotal+X-OriginalX > WidthLimit:
                    X = OriginalX
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
                    X = OriginalX
                    Y += Font['Height']
                CurrentWord = ''
            if X-OriginalX > WidthLimit:
                X = OriginalX
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
                    X = OriginalX
                    Y += Font['Height']
                CurrentWord = ''
            if X-OriginalX > WidthLimit:
                X = OriginalX
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
