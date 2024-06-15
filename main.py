import pygame
import os
import math
import random
import time

cursor_img = pygame.transform.scale(pygame.image.load(os.path.join("SHOOTING GAME","Assets","cursor.png")),(40,40))
cursor_img_rect = cursor_img.get_rect()

pygame.font.init()
pygame.mixer.init()

WIDTH = 1000
HEIGHT = 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Secret Wars")

WHITE = (255, 255, 255)
RED = (250, 0, 0)

BG_IMAGE = pygame.image.load(os.path.join("SHOOTING GAME","Assets", "CityBG.png"))
BG = pygame.transform.scale(BG_IMAGE, (WIDTH, HEIGHT))

MAINCHAR_IMAGE = pygame.image.load(os.path.join("SHOOTING GAME","Assets", "MainCharacter.png"))
MAINCHAR = pygame.transform.scale(MAINCHAR_IMAGE, (150, 300))

SHOTGUN_IMAGE = pygame.image.load(os.path.join("SHOOTING GAME","Assets", "Shotgun.png"))
SHOTGUN = pygame.transform.scale(SHOTGUN_IMAGE, (130,100)).convert_alpha()
shotgun_x = 200
shotgun_y = 270

BULLET_SHOOTING_IMAGE = pygame.image.load(os.path.join("SHOOTING GAME","Assets", "BULLET_SHOOTING.png"))
BULLET_SHOOTING = pygame.transform.scale(BULLET_SHOOTING_IMAGE, (50, 50))

BULLET_SHOOTING_SOUND = pygame.mixer.Sound(os.path.join("SHOOTING GAME","Assets","gunshot.mp3"))
ENEMY_BLAST_SOUND = pygame.mixer.Sound(os.path.join("SHOOTING GAME","Assets","explosion.mp3"))

ENEMY_WIDTH = 150
ENEMY_HEIGHT = 180
ENEMY_IMAGE = pygame.image.load(os.path.join("SHOOTING GAME","Assets", "Enemy.png"))
ENEMY = pygame.transform.scale(ENEMY_IMAGE, (ENEMY_WIDTH, ENEMY_HEIGHT))

SCORE_FONT = pygame.font.SysFont("comicsans", 40)
FINAL_FONT = pygame.font.SysFont("comicsans", 40)

LIVES = 3
POINTS = 0

FPS = 60

def draw_window(shotgun, shotgun_rect, bullets, position_x_list, position_y_list, ENEMY_rect_list):
    global POINTS
    WIN.fill(WHITE)
    WIN.blit(BG, (0, 0))
    point_text = SCORE_FONT.render("SCORE : " + str(POINTS), 1, WHITE)
    lives_text = SCORE_FONT.render("LIVES : " + str(LIVES), 1, WHITE)
    WIN.blit(point_text, (10, 10))
    WIN.blit(lives_text, (WIDTH - pygame.Surface.get_width(lives_text) - 10, 10))
    WIN.blit(MAINCHAR, (100, 150))

    # Collision detection and removal of enemies
    enemies_to_remove = []
    bullets_to_remove = []
    for i in range(len(position_x_list)):
        enemy_rect = pygame.Rect(position_x_list[i], position_y_list[i], ENEMY_WIDTH, ENEMY_HEIGHT)
        for bullet in bullets:
            bullet_rect = bullet
            if bullet_rect.colliderect(enemy_rect):
                bullets_to_remove.append(bullet)
                enemies_to_remove.append(i)
                POINTS += 1  # Increase score
                ENEMY_BLAST_SOUND.play()
                break  # Exit the inner loop once a collision is detected
        if position_y_list[i] < HEIGHT:  # Check if the enemy is still visible on the screen
            position_y_list[i] += 3  # Update the y-coordinate only if the enemy is not hit
        else:
            enemies_to_remove.append(i)

    # Remove collided enemies and bullets
    for idx in sorted(enemies_to_remove, reverse=True):
        del position_x_list[idx]
        del position_y_list[idx]
        del ENEMY_rect_list[idx]
    for bullet in bullets_to_remove:
        bullets.remove(bullet)

    # Blit remaining bullets and enemies
    for bullet in bullets:
        pygame.draw.rect(WIN, RED, bullet)
        WIN.blit(BULLET_SHOOTING, (bullet.x - 15, bullet.y - 15))
    for i in range(len(position_x_list)):
        WIN.blit(ENEMY, (position_x_list[i], position_y_list[i]))
    WIN.blit(shotgun, shotgun_rect)
    cursor_img_rect.center = pygame.mouse.get_pos() 
    WIN.blit(cursor_img, cursor_img_rect)
    pygame.display.update()


def shotgun_movement(pos):
    x_dist = pos[0] - shotgun_x
    y_dist = -(pos[1] - shotgun_y)
    angle = math.degrees(math.atan2(y_dist, x_dist))
    if angle <= 120 and angle >= -70:
        shotgun = pygame.transform.rotate(SHOTGUN, angle - 50)
        shotgun_rect = shotgun.get_rect(center=(shotgun_x, shotgun_y))
    else:
        shotgun = pygame.transform.rotate(SHOTGUN, 50)
        shotgun_rect = shotgun.get_rect(center=(shotgun_x, shotgun_y))
    return shotgun, shotgun_rect

def handle_bullets(bullets, initial_direction,difficulty):
    global LIVES
    for bullet in bullets:
        # Move the bullet according to the initial direction
        bullet.x += int(initial_direction[0] * 10)  # Ensure the values are integers
        bullet.y += int(initial_direction[1] * 10)  # Ensure the values are integers
    # Remove bullets that are out of bounds
    for bullet in bullets[:]:
        if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
            bullets.remove(bullet)
            if difficulty == "HARD" or difficulty == "MEDIUM":
                LIVES -= 1

def check_hit(bullets, ENEMY_rect_list, position_x_list, position_y_list):
    bullets_to_remove = []  # Create a list to store bullets to remove
    enemies_to_remove = []  # Create a list to store enemies to remove

    # Iterate over each enemy rectangle
    for i, ENEMY_rect in enumerate(ENEMY_rect_list):
        # Iterate over each bullet
        for j, bullet in enumerate(bullets):
            # Check for collision between bullet and enemy rectangle
            if bullet.colliderect(ENEMY_rect):
                # If collision detected, post a HIT event and mark bullet for removal
                bullets_to_remove.append(j)
                # If enemy has multiple collision rectangles, only remove once
                if ENEMY_rect.x == position_x_list[i] and ENEMY_rect.y == position_y_list[i]:
                    enemies_to_remove.append(i)

    # Remove marked bullets in reverse order to avoid index issues
    for idx in reversed(bullets_to_remove):
        del bullets[idx]

    # Remove marked enemies in reverse order to avoid index issues
    for idx in reversed(enemies_to_remove):
        del ENEMY_rect_list[idx]
        del position_x_list[idx]
        del position_y_list[idx]

def check_lives(position_x_list, position_y_list):
    global LIVES
    # Iterate over a copy of position_y_list
    for position_y in position_y_list.copy():
        if position_y >= HEIGHT:
            LIVES -= 1
            # Find the index of position_y in the original position_y_list
            index = position_y_list.index(position_y)
            # Remove the enemy's position from both lists
            del position_x_list[index]
            position_y_list.remove(position_y)
        
def start_menu():
    start = True
    f = open("SHOOTING GAME\\score.txt","r")
    max_scor = f.read()
    f.close()
    while start:
        WIN.fill(WHITE)
        WIN.blit(BG,(0,0))
        easy = SCORE_FONT.render("EASY",1,WHITE)
        medium = SCORE_FONT.render("MEDIUM",1,WHITE)
        hard = SCORE_FONT.render("HARD",1,WHITE)
        easy_rect = pygame.Rect(WIDTH/2-pygame.Surface.get_width(medium)-40,HEIGHT/2-pygame.Surface.get_height(easy)/2,pygame.Surface.get_width(easy),pygame.Surface.get_height(easy))
        medium_rect = pygame.Rect(WIDTH/2-90,HEIGHT/2-pygame.Surface.get_height(easy)/2,pygame.Surface.get_width(medium),pygame.Surface.get_height(medium))
        hard_rect = pygame.Rect(WIDTH/2+110,HEIGHT/2-pygame.Surface.get_height(easy)/2,pygame.Surface.get_width(hard),pygame.Surface.get_height(hard))
        max_score = SCORE_FONT.render("MAXIMUM SCORE: "+ max_scor,1,WHITE)
        WIN.blit(max_score,(WIDTH//2-pygame.Surface.get_width(max_score)//2,HEIGHT//2-pygame.Surface.get_height(max_score)//2+150))
        WIN.blit(easy,(WIDTH/2-pygame.Surface.get_width(medium)-40,HEIGHT/2-pygame.Surface.get_height(easy)/2))
        WIN.blit(medium,(WIDTH/2-pygame.Surface.get_width(medium)/2,HEIGHT/2-pygame.Surface.get_height(medium)/2))
        WIN.blit(hard,(WIDTH/2+pygame.Surface.get_width(medium)/2+20,HEIGHT/2-pygame.Surface.get_height(medium)/2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_rect.collidepoint(pygame.mouse.get_pos()) == 1:
                    return "EASY"
                if medium_rect.collidepoint(pygame.mouse.get_pos()) == 1:
                    return "MEDIUM"
                if hard_rect.collidepoint(pygame.mouse.get_pos()) == 1:
                    return "HARD"
        pygame.display.update()

def main(difficulty):
    global LIVES, POINTS
    f = open("SHOOTING GAME\\score.txt","r")
    pygame.mouse.set_visible(False)
    run = True
    clock = pygame.time.Clock()
    bullets = []
    position_x_list = []
    position_y_list = []
    position_y = -pygame.Surface.get_height(ENEMY)
    ENEMY_rect_list = []
    count = 0
    initial_direction = None  # Store the initial direction of the bullet
    while run:
        pos = pygame.mouse.get_pos()
        clock.tick(FPS)
        count += 1
        check_lives(position_x_list,position_y_list)
        if LIVES <= 0:
            text = FINAL_FONT.render("FINAL SCORE: " + str(POINTS), 1, WHITE)
            draw_window(shotgun[0], shotgun[1], bullets, position_x_list, position_y_list, ENEMY_rect_list)
            WIN.blit(text,(WIDTH/2-pygame.Surface.get_width(text)/2,HEIGHT/2-pygame.Surface.get_height(text)/2))
            pygame.display.update()
            score = int(f.read())
            f.close()
            if POINTS>score:
                f = open("SHOOTING GAME\\score.txt","w")
                f.write(str(POINTS))
                f.close()
            time.sleep(3)
            run = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and len(bullets)<3:
                x, y = pygame.mouse.get_pos()
                bullet = pygame.Rect(shotgun_x - 5, shotgun_y - 10, 20, 20)
                bullets.append(bullet)
                # Calculate the initial direction of the bullet when fired
                x_dist = x - shotgun_x
                y_dist = y - shotgun_y
                h_dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
                if h_dist != 0:
                    x_dist /= h_dist
                    y_dist /= h_dist
                initial_direction = (x_dist, y_dist)
                BULLET_SHOOTING_SOUND.play()
        if difficulty == "EASY":
            speed = 169
        elif difficulty == "MEDIUM":
            speed = 80
        elif difficulty == "HARD":
            speed = 60
        if count % speed == 0 or count == 1:
            position_x = random.randrange(300, WIDTH - pygame.Surface.get_width(ENEMY))
            ENEMY_rect = pygame.Rect(position_x, position_y, ENEMY_WIDTH, ENEMY_HEIGHT)
            ENEMY_rect_list.append(ENEMY_rect)
            position_x_list.append(position_x)
            position_y_list.append(position_y)

        shotgun = shotgun_movement(pos)
        handle_bullets(bullets, initial_direction,difficulty)
        check_hit(bullets, ENEMY_rect_list, position_x_list, position_y_list)
        draw_window(shotgun[0], shotgun[1], bullets, position_x_list, position_y_list, ENEMY_rect_list)

def end_menu():
    captions = ["CAPTIONS",
                "MADE BY JATIN MANGTANI PRIYANI"]
    end = True
    win_height = HEIGHT
    while end:
        WIN.blit(BG,(0,0))
        caption_gap = 0
        for caption in captions:
            WIN.blit(SCORE_FONT.render(caption,1, WHITE),(WIDTH/2-pygame.Surface.get_width(SCORE_FONT.render(caption,1, WHITE))/2,win_height+caption_gap))
            caption_gap += 100
            if (win_height+caption_gap+pygame.Surface.get_height(SCORE_FONT.render(caption,1, WHITE))) < 0 and (captions[-1] == caption):
                time.sleep(2)
                end = False
        for event in pygame.event.get():
           if event.type == pygame.QUIT:
               pygame.quit()
               end = False
        win_height -= 1
        pygame.display.update()

if __name__ == "__main__":
    difficulty = start_menu()
    main(difficulty)
    end_menu()