import pygame
import os

WIDTH,HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invaders")

WHITE = (255,255,255)


FPS = 60
VEL = 5
BULLET_VEL = 9
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

ENEMY_HIT = pygame.USEREVENT+1
USER_HIT = pygame.USEREVENT+2

SPACESHIP_IMAGE = pygame.image.load(os.path.join("Assets","spaceship_red.png"))

SPACESHIP= pygame.transform.rotate(pygame.transform.scale(SPACESHIP_IMAGE,(SPACESHIP_WIDTH,SPACESHIP_HEIGHT)),180)

def draw_window(spaceship):
    WIN.fill(WHITE)
    WIN.blit(SPACESHIP,(spaceship.x,spaceship.y))
    pygame.display.update()

def spaceship_movement(keys_pressed,spaceship):
    global VEL
    if keys_pressed[pygame.K_a] and spaceship.x-VEL > 0: #left
        spaceship.x -= VEL
    if keys_pressed[pygame.K_d] and spaceship.x+VEL+spaceship.width < WIDTH: #right
        spaceship.x += VEL
    if keys_pressed[pygame.K_w] and spaceship.y-VEL > 0: #up
        spaceship.y -= VEL
    if keys_pressed[pygame.K_s] and spaceship.y+VEL+spaceship.height < HEIGHT: #down
        spaceship.y += VEL
    if keys_pressed[pygame.K_LSHIFT]: #boost        
        VEL = 7
    elif VEL == 7:
        VEL = 5

def handle_player_bullets(keys_pressed,spaceship):
    player_bullets = []
    if keys_pressed[pygame.K_SPACE]:
        bullet = pygame.Rect(spaceship.x + spaceship.width,spaceship.y + spaceship.height/2, 10, 5)
        player_bullets.append(bullet)
    
    for bullet in player_bullets:
        bullet.y -= BULLET_VEL



def main():
    spaceship = pygame.Rect(430,450,SPACESHIP_WIDTH,SPACESHIP_HEIGHT)


    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys_pressed = pygame.key.get_pressed()
        spaceship_movement(keys_pressed,spaceship)
        
        handle_player_bullets(keys_pressed,spaceship)
        draw_window(spaceship)


    pygame.quit()


if __name__ == "__main__":
    main()