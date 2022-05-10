# 1945
# Version 1.0
# Shoot the enemy planes
# Haroon Khalid

from calendar import c
import time
import pygame
import random
import sys
import math

# some change 

# INITIALIZE PYGAME
pygame.init()

# SET WINDOW CAPTION
pygame.display.set_caption("1945")

# SET WINDOW RESOLUTION
resolution = (320, 480)
screen = pygame.display.set_mode(resolution, 0, 32)

# SET UP LISTS
enemies = []
shots = []
explosions = []
players = []
background = []
waters = []


class Animation:

    # data = [ [time, image], [time, image], ...]

    def __init__(self, repeat, data):
        self.data = data
        self.cur_frame = 0
        self.ticks = pygame.time.get_ticks()
        self.ticks_remaining = data[0][0]
        self.pos = [0, 0]
        self.frames = (len(self.data) - 1)
        self.repeat = repeat
        self.pause = 0

    def draw(self, dest):
        old_ticks = self.ticks
        self.ticks = pygame.time.get_ticks()
        tick_difference = self.ticks - old_ticks
        self.ticks_remaining -= tick_difference

        while (self.ticks_remaining <= 0):
            self.cur_frame += 1

            if self.cur_frame > self.frames and self.repeat == 0:
                self.pause = 1
                break

            self.cur_frame %= len(self.data)
            self.ticks_remaining += self.data[self.cur_frame][0]

        if self.pause == 0:
            dest.blit(self.data[self.cur_frame][1], self.pos)


class Player(object):
    def __init__(self):
        self.image = p1_plane_1
        self.rect = self.image.get_rect()
        self.rect.x = 130
        self.rect.y = 350
        self.flying = Animation(
            1, [[30, p1_plane_1], [30, p1_plane_2], [30, p1_plane_3]])
        self.anim = self.flying
        self.shots = 0
        self.score = 0
        self.hits = 0
        self.lives = 3
        self.bombs = 3
        self.missiles = 4

    def draw(self, dest):
        self.anim.pos = self.rect
        self.anim.draw(dest)

    def update(self):

        # Get the current key state.
        key = pygame.key.get_pressed()

        # Move left/right
        if key[pygame.K_LEFT] or key[pygame.K_a]:
            self.rect.x -= 5
        if key[pygame.K_RIGHT] or key[pygame.K_d]:
            self.rect.x += 5
        if key[pygame.K_UP] or key[pygame.K_w]:
            self.rect.y -= 5
        if key[pygame.K_DOWN] or key[pygame.K_s]:
            self.rect.y += 5

        self.draw(screen)


class Explosion(object):
    def __init__(self, type):
        self.image = explode_1
        self.rect = self.image.get_rect()
        self.exploding = Animation(0, [[50, explode_1], [50, explode_2], [50, explode_3], [
                                   50, explode_4], [50, explode_5], [50, explode_6]])
        self.p1_exploding = Animation(0, [[50, p1_explode_1], [50, p1_explode_2], [50, p1_explode_3], [
                                      50, p1_explode_4], [50, p1_explode_5], [50, p1_explode_6], [50, p1_explode_7]])
        self.anim = self.exploding
        self.type = type

    def draw(self, dest):
        if self.type == 1:
            self.anim = self.p1_exploding
        self.anim.pos = self.rect
        self.anim.draw(dest)

    def update(self):
        self.draw(screen)


class Enemy(object):
    def __init__(self):
        self.image = e_plane_1
        self.rect = self.image.get_rect()
        self.rect.x = 130
        self.rect.y = 30
        self.flying = Animation(
            1, [[30, e_plane_1], [30, e_plane_2], [30, e_plane_3]])
        self.anim = self.flying

    def draw(self, dest):
        self.anim.pos = self.rect
        self.anim.draw(dest)

    def update(self):
        if self.rect.y > 100 and self.rect.y < 104:
            create_shot(1, self.rect.x, self.rect.y)
        if self.rect.y > 450:
            enemies.remove(self)

        self.rect.y += 3
        self.draw(screen)


class Water(object):
    def __init__(self):
        self.image = water_bg_ext
        self.x = 0
        self.y = -32

    def update(self):
        if self.y > 0:
            self.y = -32
        self.y += 1
        screen.blit(self.image, (self.x, self.y))


class Fire(object):
    def __init__(self, type):
        self.image = fire_1
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 100
        self.firing_1 = Animation(1, [[50, fire_1]])
        self.e_firing = Animation(1, [[50, e_shot]])
        self.anim = self.firing_1
        self.type = type

    def draw(self, dest):
        self.anim.pos = self.rect
        self.anim.draw(dest)

    def update(self):
        if self.type == 1:
            self.anim = self.e_firing
            self.rect.y += 5
            self.draw(screen)
        else:
            self.rect.y -= 20
            self.draw(screen)

class Missile(object):
    def __init__(self, type, x, y):
        self.image = missile_1
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.firing_1 = Animation(1, [[50, missile_1]])
        self.e_firing = Animation(1, [[50, missile_1]])
        self.anim = self.firing_1
        self.type = type

    def draw(self, dest):
        self.anim.pos = self.rect
        self.anim.draw(dest)

    def update(self):
        if self.type == 1:
            self.anim = self.e_firing
            self.rect.y += 5
            self.draw(screen)
        else:
            x_dist, y_dist, angle = self.guidance()
            self.rect.y -= y_dist # y_dist calculated in guidance 20
            self.rect.x -= x_dist #x_dist in guidance
            # rotate missle to angle????
            self.missle_rotate(angle)
            self.draw(screen)

    def missle_rotate(self, angle=0):
        self.image = pygame.transform.rotate(self.image, angle)
        self.firing_1 = Animation(1, [[50, self.image]])
        self.e_firing = Animation(1, [[50, self.image]])
        self.anim = self.firing_1

    def guidance(self):
        c=7586347375346385477657564576576766348756
        cm  = None
        angle = 0   
        x_dist = 0
        y_dist = 0 # default distances
        x= self.rect.x
        y= self.rect.y
        #print(f"Our missile position:  {x}, {y}")
        for e in enemies:
            ex = e.rect.center[0]
            ey = e.rect.center[1]
            if ey<0:
                continue
            x_distance = x - ex
            y_distance = y - ey
            dist = math.sqrt(x_distance**2+y_distance**2)
            # print(f"Enemy postion: {ex}, {ey}   Distance: {dist}")
            if dist==0:
                continue
            if dist<c:
                c = dist
                cm = e
                x_dist = x_distance * (2/c)
                y_dist = y_distance * (2/c)
                angle = math.asin(y_distance/c)
                
        #print(f"Closest Enemy Distance: {c}")
        return x_dist, y_dist, angle


class Bomb(object):
    def __init__(self, type):
        self.image = p1_bomb
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 100
        self.firing_1 = Animation(1, [[50, p1_bomb]])
        self.e_firing = Animation(1, [[50, p1_bomb]])
        self.anim = self.firing_1
        self.type = type

    def draw(self, dest):
        self.anim.pos = self.rect
        self.anim.draw(dest)

    def update(self):
        if self.type == 1:
            self.anim = self.e_firing
            self.rect.y += 5
            self.draw(screen)
        else:
            self.rect.y -= 20
            self.draw(screen)


class Background(object):
    def __init__(self):
        self.image_1 = background_1
        self.image_2 = background_2
        self.image_3 = background_3
        self.x = 100
        self.y = 100
        self.image = self.image_1

    def update(self):
        if self.y > 480:
            background.remove(self)
            create_background()
        self.y += 0.4
        screen.blit(self.image, (self.x, self.y))
        print(str(len(background)))


class Menu(object):
    def __init__(self):
        self.press = Animation(1, [[500, press_start_1], [200, press_start_2]])
        self.anim = self.press
        self.exit = 0

    def draw(self, dest):
        self.anim.pos = (80, 250)
        self.anim.draw(dest)

    def update(self):
        screen.blit(menu_img, (0, 0))
        self.draw(screen)
        pygame.display.flip()
        pygame.time.delay(25)

class Game_Over(object):
    # TODO: finish this
    def __init__(self):
        game_over = pygame.image.load('game_over.jpg').convert()
        game_over.set_colorkey((0, 0, 0))
        game_over= pygame.transform.scale(game_over, (300,150) )
        self.press = Animation(1, [[500, game_over], [200, press_start_2]])
        self.anim = self.press
        self.exit = 0

    def draw(self, dest):
        self.anim.pos = (10, 200)
        self.anim.draw(dest)

    def update(self):
        screen.blit(menu_img, (0, 0))
        self.draw(screen)
        pygame.display.flip()
        pygame.time.delay(25)


def create_shot(type, x, y):
    if type == 1:
        f = Fire(type)
        f.rect.x = x + 13
        f.rect.y = y + 71
        shots.append(f)
    else:
        f = Fire(type)
        f.rect.x = players[0].rect.x + 17
        f.rect.y = players[0].rect.y - 20
        shots.append(f)

# def create_bomb(type, x, y):
    # if type == 1:
    #     f = Bomb(type)
    #     f.rect.x = x + 13
    #     f.rect.y = y + 100
    #     f.rect.width = 100
    #     f.rect.height = 100
    #     shots.append(f)
    # else:
    #     f = Bomb(type)
    #     f.rect.x = players[0].rect.x + 17
    #     f.rect.y = players[0].rect.y - 101
    #     f.rect.width = 500
    #     f.rect.height = 100
    #     shots.append(f)

def missile_fire(type, x, y):
    if type == 1:
        f = Missile(type, x+13, y+100)
        shots.append(f)
    else:
        x = players[0].rect.x + 17
        y = players[0].rect.y - 101
        f = Missile(type, x, y)

        shots.append(f)

def update_shots():
    for f in shots:
        f.update()


def update_players():
    for p in players:
        p.update()


def create_enemy():
    e = Enemy()
    random.seed()
    e.rect.x = random.randrange(10, 300)
    #e.rect.y = 10
    e.rect.y = random.randrange(-500, -10)
    enemies.append(e)


def update_enemies():
    for e in enemies:
        e.update()


def create_explosion(type, erectx, erecty):
    x = Explosion(type)
    x.rect.x = erectx
    x.rect.y = erecty
    explosions.append(x)


def update_explosions():
    for x in explosions:
        if x.exploding.pause == 1:
            explosions.remove(x)
        else:
            x.update()


def create_background():
    bg = Background()
    background.append(bg)


def update_background():
    for b in background:
        b.update()
    if len(background) == 0:
        create_background()


def create_water():
    w = Water()
    waters.append(w)


def update_water():
    for w in waters:
        w.update()
    if len(waters) == 0:
        create_water()


def draw_stats():
    p1_score_text = custom_font.render("PLAYER 1", True, white)
    high_score_text = custom_font.render("HIGH SCORE", True, gold)
    p1_points_text = custom_font.render(str(p1.score), True, light_grey)
    high_score_points = custom_font.render(str(high_score), True, light_grey)
    p1_bomb_text = custom_font.render(str(p1.bombs), True, light_grey)
    screen.blit(p1_score_text, (10, 5))
    screen.blit(high_score_text, (187, 5))
    screen.blit(p1_points_text, (10, 20))
    screen.blit(high_score_points, (187, 20))

    if p1.bombs == 3:
        screen.blit(p1_bomb, (255, 455))
        screen.blit(p1_bomb, (275, 455))
        screen.blit(p1_bomb, (295, 455))
    elif p1.bombs == 2:
        screen.blit(p1_bomb, (275, 455))
        screen.blit(p1_bomb, (295, 455))
    elif p1.bombs == 1:
        screen.blit(p1_bomb, (295, 455))

    if p1.lives == 3:
        screen.blit(p1_life, (10, 455))
        screen.blit(p1_life, (38, 455))
        screen.blit(p1_life, (66, 455))
    elif p1.lives == 2:
        screen.blit(p1_life, (10, 455))
        screen.blit(p1_life, (38, 455))
    elif p1.lives == 1:
        screen.blit(p1_life, (10, 455))


def check_hit():
    for e in enemies:
        for p in players:
            for f in shots:

                if e.rect.colliderect(f.rect):
                    p1.hits += 1
                    p1.score += 100
                    thump_snd.play()
                    create_explosion(0, e.rect.x, e.rect.y)

                    # REMOVE FROM LISTS
                    if e in enemies:
                        enemies.remove(e)
                    if f in shots:
                        shots.remove(f)

                if f.rect.colliderect(p.rect):
                    thump_snd.play()
                    create_explosion(1, p.rect.x, p.rect.y)

                    # REMOVE FROM LISTS
                    if f in shots:
                        shots.remove(f)
                    if p in players:
                        players.remove(p)
def bomb_explosion():
    global enemies
    for e in enemies:
        p1.hits += 5
        p1.score += 100
        thump_snd.play()
        create_explosion(0, e.rect.x, e.rect.y)

    # REMOVE FROM LISTS
    #if e in enemies:
    #    enemies.remove(e)
    enemies = []
                    
# CREATE PLAYER
def create_player():
    print(str(len(enemies)))
    for e in enemies:
        thump_snd.play()
        create_explosion(0, e.rect.x, e.rect.y)
        if e in enemies:
            enemies.remove(e)

    p1 = Player()
    players.append(p1)

# CREATE ENEMIES

enemy_difficulty=7
def spawn_enemies():
    if len(enemies) < enemy_difficulty:
        create_enemy()

def check_plane_hit():
    for e in enemies:
        for p in players:
            if e.rect.colliderect(p.rect):
                thump_snd.play()
                create_explosion(1, p1.rect.x, p1.rect.y)
                create_explosion(0, e.rect.x, e.rect.y)

                if e in enemies:
                    enemies.remove(e)
                if p in players:
                    players.remove(p)


# SET UP THE FONT AND COLOR
default_font = pygame.font.get_default_font()
font = pygame.font.SysFont(default_font, 20)
big_font = pygame.font.SysFont(default_font, 26)
custom_font = pygame.font.Font("imagine_font.ttf", 18)
white = (255, 255, 255)
light_grey = (191, 191, 191)
gold = (255, 215, 0)

# LOAD GRAPHICS
sprite_sheet_file = '1945_sprite_sheet.png'
sprite_sheet = pygame.image.load(sprite_sheet_file).convert()
jet1 = pygame.image.load('f35_v3.png').convert()
sprite_sheet.set_colorkey((0, 67, 171))
jet1.set_colorkey((65, 245, 64))
#p1_plane_1 = sprite_sheet.subsurface(4, 400, 65, 65)
#p1_plane_2 = sprite_sheet.subsurface(70, 400, 65, 65)
#p1_plane_3 = sprite_sheet.subsurface(136, 400, 65, 65)
p1_plane_1 = jet1
p1_plane_2 = jet1
p1_plane_3 = jet1
e_plane = pygame.image.load('mig_21.png').convert()
e_plane.set_colorkey((0, 0, 0))
e_plane= pygame.transform.scale(e_plane, (70,25) )
e_plane= pygame.transform.rotate(e_plane, 90)
e_plane_1 = e_plane
e_plane_2 = e_plane
e_plane_3 = e_plane
explode_1 = sprite_sheet.subsurface(70, 169, 32, 32)
explode_2 = sprite_sheet.subsurface(103, 169, 32, 32)
explode_3 = sprite_sheet.subsurface(
    137, 169, 31, 32)  # coordinate is off 1 pixel?
explode_4 = sprite_sheet.subsurface(169, 169, 32, 32)
explode_5 = sprite_sheet.subsurface(202, 169, 32, 32)
explode_6 = sprite_sheet.subsurface(235, 169, 32, 32)
missile_1 = pygame.image.load('missile.png').convert()
missile_1= pygame.transform.scale(missile_1, (75,23) )
missile_1= pygame.transform.rotate(missile_1, 90)
missile_1.set_colorkey((0, 0, 0))
p1_explode_1 = sprite_sheet.subsurface(4, 301, 65, 65)
p1_explode_2 = sprite_sheet.subsurface(70, 301, 65, 65)
p1_explode_3 = sprite_sheet.subsurface(136, 301, 65, 65)
p1_explode_4 = sprite_sheet.subsurface(202, 301, 65, 65)
p1_explode_5 = sprite_sheet.subsurface(268, 301, 65, 65)
p1_explode_6 = sprite_sheet.subsurface(334, 301, 65, 65)
p1_explode_7 = sprite_sheet.subsurface(400, 301, 65, 65)
press_start_1 = sprite_sheet.subsurface(414, 544, 158, 22)
press_start_2 = sprite_sheet.subsurface(4, 546, 1, 1)
e_shot = sprite_sheet.subsurface(280, 148, 9, 9)
score = sprite_sheet.subsurface(572, 178, 63, 17)
fire_1 = sprite_sheet.subsurface(37, 169, 32, 32)
p1_bomb = sprite_sheet.subsurface(279, 272, 11, 22)
p1_life = sprite_sheet.subsurface(206, 274, 23, 18)
background_1 = sprite_sheet.subsurface(103, 499, 64, 65)
background_2 = sprite_sheet.subsurface(168, 499, 23, 18)
background_3 = sprite_sheet.subsurface(233, 500, 23, 18)
menu_graphic = 'menu.png'
water_bg = 'waterbgext.png'
water_bg_ext = pygame.image.load(water_bg).convert()
menu_img = pygame.image.load(menu_graphic).convert()

explode_1.set_colorkey((0, 67, 171))
explode_2.set_colorkey((0, 67, 171))
explode_3.set_colorkey((0, 67, 171))
explode_4.set_colorkey((0, 67, 171))
explode_5.set_colorkey((0, 67, 171))
explode_6.set_colorkey((0, 67, 171))
score.set_colorkey((0, 0, 0))
fire_1.set_colorkey((0, 67, 171))
e_shot.set_colorkey((0, 67, 171))

# LOAD SOUNDS
fusion_snd = pygame.mixer.Sound('fusion.ogg')
shot_snd = pygame.mixer.Sound('shot.ogg')
thump_snd = pygame.mixer.Sound('thump.ogg')
bomb_snd = pygame.mixer.Sound('bomb_explode.ogg')
cannon_snd = pygame.mixer.Sound('cannon.ogg')
start_snd = pygame.mixer.Sound('start.ogg')
pygame.mixer.music.load('music_1.ogg')
play_musc = 1


# CREATE PLAYER
p1 = Player()
players.append(p1)

# Get highest score from file
with open('high_score.txt', 'r') as f:
    high_score = int(f.readline())

# CREATE MENU
menu_screen = Menu()
menu_screen.exit = 0
game_over_screen = Game_Over()
game_over_screen.exit = 0

# MAIN MENU LOOP
while menu_screen.exit == 0:
    for event in pygame.event.get():
        key = pygame.key.get_pressed()

        if key[pygame.K_RETURN]:
            menu_screen.exit = 1
            start_snd.play()
            break
    menu_screen.update()

# MAIN GAME LOOP
i = 0
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if len(players) > 0:
                if event.key == pygame.K_SPACE:
                    shot_snd.play()
                    create_shot(0, p1.rect.x, p1.rect.y)
                    p1.shots += 1
                if event.key == pygame.K_LCTRL and p1.bombs>=1:
                    p1.bombs -= 1
                    print(f'Number of enemies BEFORE bomb: {len(enemies)}')
                    # create_bomb(0, p1.rect.x, p1.rect.y)
                    bomb_explosion()
                    bomb_snd.play()
                    print(f'Number of enemies AFTER bomb:  {len(enemies)}')
                if event.key == pygame.K_e and p1.missiles > 0:
                    missile_fire(0, p1.rect.x, p1.rect.y)
                    p1.missiles -= 1                    
            if event.key == pygame.K_r and p1.lives>0:
                if len(players) == 0:
                    create_player()
                    p1.lives-=1

    if p1.score > high_score:
        high_score = p1.score
        with open('high_score.txt', 'w') as f:
            f.write(str(high_score))
    if play_musc == 1:
        #pygame.mixer.music.play()
        pass
    play_musc = 0
    screen.fill((0, 67, 171))
    # update_background()
    update_water()
    update_players()
    if i%10 == 0:
        spawn_enemies()
    update_enemies()
    update_shots()
    update_explosions()
    check_hit()
    check_plane_hit()
    draw_stats()

    if p1.lives==1 and len(players) == 0:
        while game_over_screen.exit == 0:
            for event in pygame.event.get():
                key = pygame.key.get_pressed()

                if key[pygame.K_RETURN]:
                    game_over_screen.exit = 1
                    start_snd.play()
                    pygame.time.delay(1000)
                    exit()
            game_over_screen.update()

    if i %160 == 0 and p1.missiles <4:
        p1.missiles +=1
        print(f'missile count up to {p1.missiles}')
    pygame.display.flip()
    pygame.time.delay(25)
    if i%400 == 0:
        print(f'Increasing enemy count from {enemy_difficulty} to {enemy_difficulty+1}')
        enemy_difficulty+=1
    i += 1
