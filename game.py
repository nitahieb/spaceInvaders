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
        return self.y <= height and self.y >= 0

    def collision(self, obj):
        return collide(obj,self)

class Ship:
    def __init__(self,x,y,health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None 
        self.lasers = []
        self.cool_down_counter = 0
    
    def draw(self):
        pygame.Rect(430,450,SPACESHIP_WIDTH,SPACESHIP_HEIGHT)
        WIN.blit(self.ship_img,(self.x,self.y))

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.ship_img = SPACESHIP
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.vel = VEL
        self.boost = False


class Enemy(Ship):
    COLOR_MAP = {
        "red":(RED_SPACE_SHIP,RED_LASER),
        "green":(GREEN_SPACE_SHIP,GREEN_LASER),
        "blue":(BLUE_SPACE_SHIP,BLUE_LASER)
    }


    def __init__(self ,x ,y ,color ,health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self,vel):
        self.y+= vel



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
        spaceship.vel = 10
        spaceship.boost=True
    elif spaceship.vel == 10:
        spaceship.vel = 5
        spaceship.boost = False


def handle_player_bullets(player_bullets,spaceship):
    for bullet in player_bullets:
        bullet.y -= BULLET_VEL


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x, offset_y)) != None

def main():
    #spaceship = pygame.Rect(430,450,SPACESHIP_WIDTH,SPACESHIP_HEIGHT)
    player_bullets = []
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans",30)
    lost_font = pygame.font.SysFont("comicsans",60)

    enemies = []
    wave_length = 5
    enemy_vel = 1


    clock = pygame.time.Clock()
    lost = False
    lost_count = 0
    run = True

    player = Player(430,450)

    def redraw_window():
        WIN.blit(BG,(0,0))
        
        
        if player.boost:
            WIN.blit(FIRE,(player.x+player.get_width()//2-7,player.y+player.get_height()))
        for bullet in player_bullets:
            pygame.draw.rect(WIN,BLACK,bullet)


        for enemy in enemies:
            enemy.draw()

        player.draw()
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,0,255))
        level_label = main_font.render(f"Level: {level}",1,(255,0,255))
        WIN.blit(lives_label,(10,10))
        WIN.blit(level_label,(WIDTH-level_label.get_width()-10,10))

        if lost:
            lost_label = lost_font.render("You Lost!!",1,(255,255,255))
            WIN.blit(lost_label,(WIDTH/2-lost_label.get_width()/2,150))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <=0:
            lost = True
            lost_count += 1

        if lost:
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
                run = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = pygame.Rect(player.x + player.get_width()//2-2   ,player.y + player.get_height()//2, 5, 10)
                    player_bullets.append(bullet)


        keys_pressed = pygame.key.get_pressed()
        spaceship_movement(keys_pressed,player)

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            if enemy.y+enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        
        handle_player_bullets(player_bullets,player)
        


    pygame.quit()


if __name__ == "__main__":
    main()