import pygame
import os
import random

#Loading in assets and setting constants
pygame.font.init()
pygame.mixer.init()
BGMUSIC = pygame.mixer.Sound(os.path.join("Assets","BGmusic.wav"))
LASER_SOUND= pygame.mixer.Sound(os.path.join("Assets", "laser7.wav"))
pygame.mixer.Sound.set_volume(BGMUSIC,0.3)
BGMUSIC.play(-1)

WIDTH,HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invaders")


WHITE = (255,255,255)
BLACK = (0,0,0)
FPS = 60
VEL = 5
LASER_VEL = 9
ENEMY_VEL = 1
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

ENEMY_HIT = pygame.USEREVENT+1
USER_HIT = pygame.USEREVENT+2

RED_SPACE_SHIP = pygame.image.load(os.path.join("Assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("Assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("Assets", "pixel_ship_blue_small.png"))
SPACESHIP_IMAGE = pygame.image.load(os.path.join("Assets","spaceship_red.png"))

FIRE_IMAGE = pygame.image.load(os.path.join("Assets","fire.png"))
FIRE = pygame.transform.rotate(pygame.transform.scale(FIRE_IMAGE,(SPACESHIP_WIDTH//3,SPACESHIP_HEIGHT//2+10)),180)


RED_LASER = pygame.image.load(os.path.join("Assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("Assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("Assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("Assets", "pixel_laser_yellow.png"))
BG = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "space.png")), (WIDTH, HEIGHT))

SPACESHIP= pygame.transform.rotate(pygame.transform.scale(SPACESHIP_IMAGE,(SPACESHIP_WIDTH,SPACESHIP_HEIGHT)),180)

#Laser class deals with laser object from enemies and player
class Laser:
    #initializes individual laser
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    #visualizes the laser object on the game
    def draw(self):
        WIN.blit(self.img,(self.x,self.y))

    #changes the laser objects location
    def move(self, vel):
        self.y += vel
    
    #checks if laser is off screen
    def off_screen(self,height):
        return not (self.y <= height and self.y+30 >= 0)

    #checks if a collision between two objects has happened
    def collision(self, obj):
        return collide(obj,self)

#Abstract ship class inherited by the player class and the enemy class
class Ship:
    COOLDOWN = 20
    #ship initialization
    def __init__(self,x,y,health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None 
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    
    #inputs visual representation of ship class into game
    def draw(self):
        pygame.Rect(430,450,self.x,self.y)
        WIN.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers: 
            laser.draw()

    #checks if ship is able to shoot laser if it is will set counter to 0, else continues counter
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter +=1
    
    #ship image width getter
    def get_width(self):
        return self.ship_img.get_width()

    #ship image height getter
    def get_height(self):
        return self.ship_img.get_height()

#Ship class for player, inherits Ship class
class Player(Ship):
    #Player ship initialization
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.ship_img = SPACESHIP
        self.lives = 5
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.vel = VEL
        self.boost = False

    #function deals with the handling of laser movement, deletion and collision
    def move_lasers(self,vel,objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    #function deals with checking if player is able to shoot, creates the visual and starts cooldown
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-22,self.y-self.get_height(),self.laser_img)   
            self.lasers.append(laser)
            pygame.mixer.Sound(LASER_SOUND).play()
            self.cool_down_counter = 1
    
    #Draws ship
    def draw(self):
        super().draw()
        self.healthbar()
    
    #draws ship healthbar
    def healthbar(self):
        pygame.draw.rect(WIN,(255,0,0),(self.x,self.y+self.ship_img.get_height()+10, self.ship_img.get_width(),10))
        pygame.draw.rect(WIN,(0,255,0),(self.x,self.y+self.ship_img.get_height()+10, self.ship_img.get_width()*(self.health/self.max_health),10))

    #takes input of keys pressed and moves character and shoots accordingly
    def player_commands(self,keys_pressed):
        if keys_pressed[pygame.K_SPACE]:
            self.shoot()
        if keys_pressed[pygame.K_a] and self.x-self.vel > 0: #left
            self.x -= self.vel
        if keys_pressed[pygame.K_d] and self.x+self.vel+self.get_width() < WIDTH: #right
            self.x += self.vel
        if keys_pressed[pygame.K_w] and self.y-self.vel > 0: #up
            self.y -= self.vel
        if keys_pressed[pygame.K_s] and self.y+self.vel+self.get_height() < HEIGHT: #down
            self.y += self.vel
        if keys_pressed[pygame.K_LSHIFT]: #boost        
            self.vel = 7
            self.boost=True
        elif self.vel == 7:
            self.vel = 5
            self.boost = False
    
    #checks if player has lost all health and returns new player object
    def death(self):
        if self.health <=0:
            self.health = 100
            self.lives-= 1
            self.x = 430
            self.y = 440



#Enemy ship class, inherits Ship class
class Enemy(Ship):
    #Dictionary to pick between three possible ships with three possible lasers
    COLOR_MAP = {
        "red":(RED_SPACE_SHIP,RED_LASER),
        "green":(GREEN_SPACE_SHIP,GREEN_LASER),
        "blue":(BLUE_SPACE_SHIP,BLUE_LASER)
    }

    #Initializes enemy ship
    def __init__(self ,x ,y ,color ,health=100):
        super().__init__(x, y, health)
        self.color = color
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    #takes in vel moves enemy vel amount 
    def move(self,vel):
        self.y+= vel
    
    #Function deals with enemy shooting,
    def shoot(self):
        if self.cool_down_counter == 0:
            if self.color == "blue":
                laser = Laser(self.x-25,self.y,self.laser_img)
            else:
                laser = Laser(self.x-15,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
    #function deals with enemy laser removal and collision
    def move_lasers(self,vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)


#Helper to check if two objects have collided
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x, offset_y)) != None

#Helper to maintain all enemy actions
def enemy_actions(enemies,player):
    for enemy in enemies[:]:
        enemy.move(ENEMY_VEL)
        enemy.move_lasers(LASER_VEL,player)

        if random.randrange(0, 4*FPS) == 1:
            enemy.shoot()

        if collide(enemy,player):
            player.health -= 100
            enemies.remove(enemy)
        elif enemy.y+enemy.get_height() > HEIGHT:
            player.lives -= 1
            enemies.remove(enemy)

#helper to deal with progressing levels
def level_set(enemies,level,wave_length):
    if len(enemies) == 0:
        level += 1
        wave_length +=5
        for i in range(wave_length):
            enemy = Enemy(random.randrange(50,WIDTH-50), random.randrange(-1500,-100),random.choice(["red","blue","green"]))
            enemies.append(enemy)
    return (level,wave_length)

#checks if game is over, if it is send to gameover screen
def finishgame(player,redraw_window):
    if player.lives <= 0:
        end_time=0
        start_time = pygame.time.get_ticks()
        while end_time-start_time < 3000:
            end_time = pygame.time.get_ticks()
            redraw_window(True)
        return False
    else: return True

def main():
    level = 0
    main_font = pygame.font.SysFont("comicsans",30)
    lost_font = pygame.font.SysFont("comicsans",60)
    enemies = []
    wave_length = 5
    clock = pygame.time.Clock()
    run = True
    player = Player(430,440) #places player

    #renders most of game and updates, lost input changes visuals because game over
    def redraw_window(lost):
        WIN.blit(BG,(0,0))
        if player.boost:
            WIN.blit(FIRE,(player.x+player.get_width()//2-7,player.y+player.get_height()))

        for enemy in enemies:
            enemy.draw()
        player.draw()
        lives_label = main_font.render(f"Lives: {player.lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}",1,(255,255,255))
        WIN.blit(lives_label,(10,10))
        WIN.blit(level_label,(WIDTH-level_label.get_width()-10,10))

        if lost:
            player.x = 1000
            player.y = 1000
            player.health = 0
            lost_label = lost_font.render("You Lost!!",1,(255,255,255))
            WIN.blit(lost_label,(WIDTH/2-lost_label.get_width()/2,150))

        pygame.display.update()


    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
        redraw_window(False) #draw visuals
        player.death()       #check if player died if they did adjust accordingly
        level,wave_length = level_set(enemies,level,wave_length)  #check if level complete if complete return updated level ,wave_length
        enemy_actions(enemies,player)                             #deal with all enemy actions
        player.player_commands(pygame.key.get_pressed())          #deal with player input
        player.move_lasers(-LASER_VEL,enemies)                    #deal with player lasers
        run = finishgame(player,redraw_window)                    #check if game over and send to gameover screen


#deals with all the main menu behaviour amd visuals
def main_menu():
    title_font = pygame.font.SysFont("comicsans",70)
    run = True
    while run:
        WIN.blit(BG,(0,0))
        title_label = title_font.render("Press the mouse to begin",1,(255,255,255))
        WIN.blit(title_label,(WIDTH/2 - title_label.get_width()/2,250))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    quit()

if __name__ == "__main__":
    main_menu()