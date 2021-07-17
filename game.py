import pygame
import os
import random

pygame.font.init()

WIDTH,HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invaders")

WHITE = (255,255,255)
BLACK = (0,0,0)


FPS = 60
VEL = 5
BULLET_VEL = 9
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


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self):
        WIN.blit(self.img,(self.x,self.y))

    def move(self, vel):
        self.y += vel
    
    def off_screen(self,height):
        return not (self.y <= height and self.y+30 >= 0)

    def collision(self, obj):
        return collide(obj,self)

class Ship:
    COOLDOWN = 20
    def __init__(self,x,y,health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None 
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    
    def draw(self):
        pygame.Rect(430,450,self.x,self.y)
        WIN.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers: 
            laser.draw()

    def move_lasers(self,vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter +=1
    
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-22,self.y-self.get_height(),self.laser_img)   
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.ship_img = SPACESHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.vel = VEL
        self.boost = False

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
                        self.lasers.remove(laser)
    
    def draw(self):
        super().draw()
        self.healthbar()
    
    def healthbar(self):
        pygame.draw.rect(WIN,(255,0,0),(self.x,self.y+self.ship_img.get_height()+10, self.ship_img.get_width(),10))
        pygame.draw.rect(WIN,(0,255,0),(self.x,self.y+self.ship_img.get_height()+10, self.ship_img.get_width()*(self.health/self.max_health),10))



class Enemy(Ship):
    COLOR_MAP = {
        "red":(RED_SPACE_SHIP,RED_LASER),
        "green":(GREEN_SPACE_SHIP,GREEN_LASER),
        "blue":(BLUE_SPACE_SHIP,BLUE_LASER)
    }

    def __init__(self ,x ,y ,color ,health=100):
        super().__init__(x, y, health)
        self.color = color
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self,vel):
        self.y+= vel
    
    def shoot(self):
        if self.cool_down_counter == 0:
            if self.color == "blue":
                laser = Laser(self.x-25,self.y,self.laser_img)
            else:
                laser = Laser(self.x-15,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1



def spaceship_movement(keys_pressed,spaceship):
    if keys_pressed[pygame.K_a] and spaceship.x-spaceship.vel > 0: #left
        spaceship.x -= spaceship.vel
    if keys_pressed[pygame.K_d] and spaceship.x+spaceship.vel+spaceship.get_width() < WIDTH: #right
        spaceship.x += spaceship.vel
    if keys_pressed[pygame.K_w] and spaceship.y-spaceship.vel > 0: #up
        spaceship.y -= spaceship.vel
    if keys_pressed[pygame.K_s] and spaceship.y+spaceship.vel+spaceship.get_height() < HEIGHT: #down
        spaceship.y += spaceship.vel
    if keys_pressed[pygame.K_LSHIFT]: #boost        
        spaceship.vel = 7
        spaceship.boost=True
    elif spaceship.vel == 7:
        spaceship.vel = 5
        spaceship.boost = False



def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x, offset_y)) != None

def main():
    #spaceship = pygame.Rect(430,450,SPACESHIP_WIDTH,SPACESHIP_HEIGHT)
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans",30)
    lost_font = pygame.font.SysFont("comicsans",60)

    laser_vel = 9

    enemies = []
    wave_length = 5
    enemy_vel = 1


    clock = pygame.time.Clock()
    lost = False
    lost_count = 0
    run = True

    player = Player(430,440)

    def redraw_window():
        WIN.blit(BG,(0,0))

        if player.boost:
            WIN.blit(FIRE,(player.x+player.get_width()//2-7,player.y+player.get_height()))

        for enemy in enemies:
            enemy.draw()
        player.draw()
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}",1,(255,255,255))
        WIN.blit(lives_label,(10,10))
        WIN.blit(level_label,(WIDTH-level_label.get_width()-10,10))

        if lost:
            lost_label = lost_font.render("You Lost!!",1,(255,255,255))
            WIN.blit(lost_label,(WIDTH/2-lost_label.get_width()/2,150))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0:
            lost = True
            lost_count += 1

        if player.health <=0:
            lives-= 1
            del player
            player = Player(430,440)
            player.health = 100

        if lost:
            del player
            player = Player(1000,1000)
            if(lost_count> FPS*3 ):
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length +=5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50,WIDTH-50), random.randrange(-1500,-100),random.choice(["red","blue","green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_SPACE]:
            player.shoot()
        
        spaceship_movement(keys_pressed,player)

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel,player)

            if random.randrange(0, 4*FPS) == 1:
                enemy.shoot()

            if collide(enemy,player):
                player.health -= 100
                enemies.remove(enemy)
            elif enemy.y+enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        
        player.move_lasers(-laser_vel,enemies)
        
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