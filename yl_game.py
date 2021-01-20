import pygame
from pygame.locals import *
from pygame.locals import *


# Загрузка или создани(если его нет) конфига
def loadCfg(file):
    with open(file, "r") as cfg_file:
        cfg = cfg_file.readline()

    if len(cfg) == 0:
        level = 1
        info_dead = 0
        cfg_file = open(file, 'w')
        cfg_file.write(str(level) + ';' + str(info_dead))
        cfg_file.close()
    else:
        cfg = cfg.split(';')
        level = cfg[0]
        info_dead = cfg[1]

    return level, info_dead


level, info_dead = loadCfg('cfg.txt')

# установка режима экрана
flags = FULLSCREEN | DOUBLEBUF

pygame.init()

clock = pygame.time.Clock()
fps = 60

# размер окна
infoObject = pygame.display.Info()
screen_width = infoObject.current_w
screen_height = infoObject.current_h

# размер квадрата
size_cell = screen_height // 8

dead = 0
menu = 1
screen = pygame.display.set_mode((screen_width, screen_height), flags)
pygame.display.set_caption('Platformer')

# загрузка заднего фона
bg_img = pygame.image.load('img/background.jpg')

restart_img = pygame.image.load('img/restart.png')
start_img = pygame.image.load('img/start.png')
exit_img = pygame.image.load('img/exit.png')
stop_img = pygame.image.load('img/stopt.png')
newGame_img = pygame.image.load('img/newGame.png')

level_group = []

# загрузка музыки и звуковых эффектов
pygame.mixer.music.load('music/music.mp3')
pygame.mixer.music.set_volume(0.05)
pygame.mixer.music.play(-1, 0.5, 5000)

mana_sfx = pygame.mixer.Sound('music/mana.wav')
mana_sfx.set_volume(0.5)

jump_sfx = pygame.mixer.Sound('music/jump.wav')
jump_sfx.set_volume(0.3)

newLevel_sfx = pygame.mixer.Sound('music/level.wav')
newLevel_sfx.set_volume(0.5)

gameOver_sfx = pygame.mixer.Sound('music/death.wav')
gameOver_sfx.set_volume(0.5)


# функци окргления выше на десяток(нужен для анимации)
def roundup(x):
    return x if x % 10 == 0 else x + 10 - x % 10


# очистка группы спрайтов
def delete(group):
    group.empty()


# загрузка уровней
def levelLoad(maxLevel):
    for i in range(1, maxLevel + 1):
        with open(f'level/lvl{i}.txt') as f:
            lvl = [list(map(int, row.split())) for row in f.readlines()]
        level_group.append(lvl)


# загрузка нового уровня
def new_level(lvl):
    player.reset(size_cell + 10, size_cell * 9 + 10)
    lava_group.empty()
    portal_group.empty()
    spike_group.empty()

    world = World(lvl)
    return world


# изменение режима портала
def ResetPortal():
    for i in portal_group:
        i.restart()


# класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, level, dead_num):
        # списки с разными положениями персонажа во время анимации
        self.hero_r = []
        self.hero_l = []
        # загрузка тайтлов анимации
        for i in range(1, 7):
            # оригинал
            hero_r = pygame.image.load(f'img/hero_new{i}.png')
            # изменение размеров
            hero_r = pygame.transform.scale(hero_r, (
            round(size_cell // 2), round(size_cell // 1.4)))
            # отражаю
            hero_l = pygame.transform.flip(hero_r, True, False)
            self.hero_r.append(hero_r)
            self.hero_l.append(hero_l)
        # кадр в анимации (0 - стоит)
        self.index = 0
        self.coun = 0
        self.jump_num = 0

        self.default = pygame.image.load(f'img/hero.png')
        self.image = pygame.transform.scale(self.default, (
        round(size_cell // 2), round(size_cell // 1.4)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.wid = self.image.get_width()
        self.heig = self.image.get_height()
        self.jumped = False
        self.direction = 0
        self.score = 0
        self.dead_num = dead_num

        self.level = level
        self.levelChange = 0

    def update(self, dead):
        dx = 0
        dy = 0
        # обработка нажатия клавишь
        if dead != 1:
            key = pygame.key.get_pressed()
            if key[
                pygame.K_SPACE] and self.jumped == False and self.jump_num < 2:
                jump_sfx.play()
                self.vel_y = -18
                self.jumped = True
                self.jump_num += 1
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_a]:
                dx -= 5
                self.coun += 1
                self.direction = -1
            if key[pygame.K_d]:
                dx += 5
                self.coun += 1
                self.direction = 1

            if key[pygame.K_a] == False and key[pygame.K_d] == False:
                self.coun = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.hero_r[self.index]
                    self.default = pygame.image.load(f'img/hero.png')
                    self.image = pygame.transform.scale(self.default, (
                    round(size_cell // 2), round(size_cell // 1.4)))
                if self.direction == -1:
                    self.default = pygame.image.load(f'img/hero.png')
                    self.image = pygame.transform.scale(self.default, (
                    round(size_cell // 2), round(size_cell // 1.4)))
                    self.image = pygame.transform.flip(self.image, True, False)

            # обработка анимации
            if self.coun > 5:
                self.coun = 0
                self.index += 1
                if self.index >= len(self.hero_r):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.hero_r[self.index]
                if self.direction == -1:
                    self.image = self.hero_l[self.index]

            # "гравтация"
            # коэффициент высоты прыжка
            coefficient_gravity = 1
            # скорость падения
            speed_fall = 10
            self.vel_y += coefficient_gravity
            if self.vel_y > speed_fall:
                self.vel_y = speed_fall
            dy += self.vel_y

            # столкновение с блоками
            for tile in world.tile_list:
                # столкновение по "х"
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.wid,
                                       self.heig):
                    dx = 0
                # столкновение по "у"
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.wid,
                                       self.heig):
                    self.jump_num = 0
                    # в прижке
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0

                    # падает
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0

            # столкновение с лавой
            if pygame.sprite.spritecollide(self, lava_group, False):
                gameOver_sfx.play()
                dead = 1
                self.dead_num += 1
                cfg_file = open('cfg.txt', 'w')
                cfg_file.write(
                    str(player.lvlUpdate()) + ';' + str(self.dead_num))
                cfg_file.close()

            # столкновение с врагами
            if pygame.sprite.spritecollide(self, enemy_group, False):
                gameOver_sfx.play()
                dead = 1
                self.dead_num += 1
                cfg_file = open('cfg.txt', 'w')
                cfg_file.write(
                    str(player.lvlUpdate()) + ';' + str(self.dead_num))
                cfg_file.close()

            # столкновение с собакой
            if pygame.sprite.spritecollide(self, dog_group, False):
                self.level += 1
                self.levelChange = 1

            # столкновение с шипами
            if pygame.sprite.spritecollide(self, spike_group, False):
                dead = 1
                self.dead_num += 1
                cfg_file = open('cfg.txt', 'w')
                cfg_file.write(
                    str(player.lvlUpdate()) + ';' + str(self.dead_num))
                cfg_file.close()
                gameOver_sfx.play()

            # столкновение с кускми портала
            if pygame.sprite.spritecollide(self, score_group, True):
                self.score += 1
                mana_sfx.play()

            # столкновение с порталом
            if pygame.sprite.spritecollide(self, portal_group, False):
                for i in portal_group:
                    if i.PortalMode() == 1:
                        self.level += 1
                        self.levelChange = 1

            # изменение координат персонажа
            self.rect.x += dx
            self.rect.y += dy

        # не дает персанажу выпасть за пределы мира
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            dy = 0

        screen.blit(self.image, self.rect)

        return dead

    def reset(self, x, y):
        # списки с разными положениями персонажа во время анимации
        self.hero_r = []
        self.hero_l = []
        # загрузка тайтлов анимации
        for i in range(1, 7):
            # оригинал
            hero_r = pygame.image.load(f'img/hero_new{i}.png')
            # изменение размеров
            hero_r = pygame.transform.scale(hero_r, (
            round(size_cell // 2), round(size_cell // 1.4)))
            # отражаю
            hero_l = pygame.transform.flip(hero_r, True, False)
            self.hero_r.append(hero_r)
            self.hero_l.append(hero_l)
        # кадр в анимации (0 - стоит)
        self.index = 0
        self.coun = 0

        self.image = self.hero_r[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.wid = self.image.get_width()
        self.heig = self.image.get_height()
        self.jumped = False
        self.direction = 0
        self.score = 0

        self.levelChange = 0

    # возврат номера уровня
    def lvlUpdate(self):
        return self.level

    # воврат изменен ли уровень
    def lvlChange(self):
        return self.levelChange

    def ScoreUpdate(self):
        return self.score

    # колличество смерте
    def deadInfo(self):
        return self.dead_num


# класс мира
class World():
    def __init__(self, data):
        self.tile_list = []

        # загрузка текстур
        self.dirt_img = pygame.image.load('img/dirt.png')
        self.road_img = pygame.image.load('img/road.png')
        self.angle_img = pygame.image.load('img/angle.png')
        self.angleLeft_img = pygame.image.load('img/angle2.png')
        self.wallLeft_img = pygame.image.load('img/wall_left.png')
        self.wallRight_img = pygame.image.load('img/wall_rightt.png')
        self.roof_img = pygame.image.load('img/rooft.png')
        self.fly_img = pygame.image.load('img/fly.png')
        self.flyLeft_img = pygame.image.load('img/fly_leftl.png')
        self.flyRight_img = pygame.image.load('img/fly_right.png')
        self.flyAll_img = pygame.image.load('img/fly_all.png')
        self.dog_img = pygame.image.load('img/dog.png')

        self.data = data

        # чтобы не рисовать в ручную каждую "ячейку" использу матрицу с информацией о уровне
        # позволит добавить множество разных текстур и быстро создавать уровни в игре
        row = 0
        for i in self.data:
            col = 0
            for j in i:
                # 1 - блок грязи
                if j == 1:
                    # изменяю размер под заданый размер
                    img = pygame.transform.scale(self.dirt_img,
                                                 (size_cell, size_cell))
                    # создаю rect обьект
                    img_rect = img.get_rect()
                    # изменяю его координаты по его положению в матрице
                    img_rect.x = col * size_cell
                    img_rect.y = row * size_cell
                    j = (img, img_rect)
                    self.tile_list.append(j)
                # 2 - блок дорожки
                if j == 2:
                    img = pygame.transform.scale(self.road_img,
                                                 (size_cell, size_cell))
                    img_rect = img.get_rect()
                    img_rect.x = col * size_cell
                    img_rect.y = row * size_cell
                    j = (img, img_rect)
                    self.tile_list.append(j)

                # 4 - лава
                if j == 4:
                    lava = LavaBlock(col * size_cell,
                                     row * size_cell + (size_cell // 4))
                    lava_group.add(lava)
                # 5 - шипы
                if j == 5:
                    spike = SpikeBlock(col * size_cell, row * size_cell)
                    spike_group.add(spike)
                # 6 - угол
                if j == 6:
                    img = pygame.transform.scale(self.angle_img,
                                                 (size_cell, size_cell))
                    img_rect = img.get_rect()
                    img_rect.x = col * size_cell
                    img_rect.y = row * size_cell
                    j = (img, img_rect)
                    self.tile_list.append(j)
                # 66 - угол(левый)
                if j == 66:
                    img = pygame.transform.scale(self.angleLeft_img,
                                                 (size_cell, size_cell))
                    img_rect = img.get_rect()
                    img_rect.x = col * size_cell
                    img_rect.y = row * size_cell
                    j = (img, img_rect)
                    self.tile_list.append(j)
                # 8 - стена(левая)
                if j == 8:
                    img = pygame.transform.scale(self.wallLeft_img,
                                                 (size_cell, size_cell))
                    img_rect = img.get_rect()
                    img_rect.x = col * size_cell
                    img_rect.y = row * size_cell
                    j = (img, img_rect)
                    self.tile_list.append(j)
                # 11 - стена(правая)
                if j == 11:
                    img = pygame.transform.scale(self.wallRight_img,
                                                 (size_cell, size_cell))
                    img_rect = img.get_rect()
                    img_rect.x = col * size_cell
                    img_rect.y = row * size_cell
                    j = (img, img_rect)
                    self.tile_list.append(j)
                # 12 - верхняя стена
                if j == 12:
                    img = pygame.transform.scale(self.roof_img,
                                                 (size_cell, size_cell))
                    img_rect = img.get_rect()
                    img_rect.x = col * size_cell
                    img_rect.y = row * size_cell
                    j = (img, img_rect)
                    self.tile_list.append(j)
                # 13 - летающая платформа(стандарт)
                if j == 13:
                    img = pygame.transform.scale(self.fly_img,
                                                 (size_cell, size_cell))
                    img_rect = img.get_rect()
                    img_rect.x = col * size_cell
                    img_rect.y = row * size_cell
                    j = (img, img_rect)
                    self.tile_list.append(j)
                # 14 - летающая платформа(правая)
                if j == 14:
                    img = pygame.transform.scale(self.flyRight_img,
                                                 (size_cell, size_cell))
                    img_rect = img.get_rect()
                    img_rect.x = col * size_cell
                    img_rect.y = row * size_cell
                    j = (img, img_rect)
                    self.tile_list.append(j)
                # 15 - летающая платформа(левая)
                if j == 15:
                    img = pygame.transform.scale(self.flyLeft_img,
                                                 (size_cell, size_cell))
                    img_rect = img.get_rect()
                    img_rect.x = col * size_cell
                    img_rect.y = row * size_cell
                    j = (img, img_rect)
                    self.tile_list.append(j)
                # 16 - летающая платформа(левая)
                if j == 16:
                    img = pygame.transform.scale(self.flyAll_img,
                                                 (size_cell, size_cell))
                    img_rect = img.get_rect()
                    img_rect.x = col * size_cell
                    img_rect.y = row * size_cell
                    j = (img, img_rect)
                    self.tile_list.append(j)
                # 44 - собака
                if j == 44:
                    dog = DogBlock(col * size_cell, row * size_cell)
                    dog_group.add(dog)
                # 9 - портал(лево)
                if j == 9:
                    portal = PortalBlock(col * size_cell, row * size_cell)
                    portal_group.add(portal)
                # 9 - портал(право)
                if j == 99:
                    portal = PortalBlock(col * size_cell, row * size_cell, True)
                    portal_group.add(portal)

                col += 1
            row += 1

    def reset(self):
        row = 0
        for i in self.data:
            col = 0
            for j in i:
                # 6 - мана
                if j == 7:
                    mana = ManaBlock(col * size_cell, row * size_cell)
                    score_group.add(mana)
                # 22 - враг
                if j == 22:
                    enemy = Enemy(col * size_cell, row * size_cell)
                    enemy_group.add(enemy)
                col += 1
            row += 1

    # вывод мира на жкран
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


# класс лавы
class LavaBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.con = 1

        # списки с разными положениями персонажа во время анимации
        self.lava = []
        # загрузка тайтлов анимации
        for i in range(1, 5):
            # оригинал
            lava_img = pygame.image.load(f'img/lava{i}.png')
            # изменение размеров
            lava_img = pygame.transform.scale(lava_img, (size_cell, size_cell))
            self.lava.append(lava_img)

        img = pygame.image.load('img/lava1.png')
        self.image = pygame.transform.scale(img, (size_cell, size_cell))
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.x = x
        self.y = y

    # анимация
    def animation(self):
        # расчет по кадрам
        # каждлые 10 фпс, новый фрейм анимации
        if self.con < 41:
            img = pygame.image.load(f'img/lava{roundup(self.con) // 10}.png')
            self.image = pygame.transform.scale(img, (size_cell, size_cell))
            self.rect = self.image.get_rect()

            self.rect.x = self.x
            self.rect.y = self.y
        else:
            self.con = 1

            img = pygame.image.load(f'img/lava{self.con}.png')
            self.image = pygame.transform.scale(img, (size_cell, size_cell))
            self.rect = self.image.get_rect()

            self.rect.x = self.x
            self.rect.y = self.y
        self.con += 1


# блок шипов
class SpikeBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/spike_active.png')
        self.image = pygame.transform.scale(img, (size_cell, size_cell + 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - 52


# блок собаки
class DogBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/dog.png')
        self.image = pygame.transform.scale(img, (size_cell, size_cell + 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# блок портала
class PortalBlock(pygame.sprite.Sprite):
    def __init__(self, x, y, flip=False):
        self.mode = 0
        self.x = x
        self.y = y
        self.mode = 0
        self.flip = flip
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/portal_dis.png')
        if self.flip:
            self.image = pygame.transform.scale(img,
                                                (size_cell, size_cell + 40))
            self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.image = pygame.transform.scale(img,
                                                (size_cell, size_cell + 40))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y - 40

    def PortalReset(self):
        self.mode = 1
        portal_group.empty()
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/portal_active.png')
        if self.flip:
            self.image = pygame.transform.scale(img,
                                                (size_cell, size_cell + 40))
            self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.image = pygame.transform.scale(img,
                                                (size_cell, size_cell + 40))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y - 40
        portal_group.add(self)

    def PortalMode(self):
        return self.mode

    def restart(self):
        self.mode = 0
        portal_group.empty()
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/portal_dis.png')
        if self.flip:
            self.image = pygame.transform.scale(img,
                                                (size_cell, size_cell + 40))
            self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.image = pygame.transform.scale(img,
                                                (size_cell, size_cell + 40))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y - 40
        portal_group.add(self)


# блок кусочка портала
class ManaBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.con = 0
        self.x = x
        self.y = y
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/mana.png')
        self.image = pygame.transform.scale(img,
                                            (size_cell // 3, size_cell // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x + size_cell // 4
        self.rect.y = y + size_cell // 3

    def animation(self):
        if self.con <= 25:
            self.rect.x = self.x + size_cell // 4
            self.rect.y = self.y + size_cell // 3 + 10
        elif self.con > 25 and self.con < 50:
            self.rect.x = self.x + size_cell // 4
            self.rect.y = self.y + size_cell // 3
        else:
            self.con = 0
        self.con += 1


# блок врага
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/enemy.png')
        self.image = pygame.transform.scale(img, (
        int(size_cell * 0.8), int(size_cell * 0.8)))
        self.rect = self.image.get_rect()
        self.rect.x = x - int(size_cell * 0.2)
        self.rect.y = y + int(size_cell * 0.2)
        self.move_dir = 1
        self.move_coun = 0

    def update(self):
        self.rect.x += self.move_dir
        self.move_coun += 1
        if abs(self.move_coun) > 50:
            self.move_dir *= -1
            self.move_coun *= -1


# класс кнопок
class Button():
    def __init__(self, x, y, image, bg=True):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.push = False
        self.bg = bg

    def draw(self):
        ret = False

        # позиция мышки
        pos = pygame.mouse.get_pos()

        # нажатии мышки
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.push == False:
                ret = True
                self.push = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.push = False

        # отрисовка кнопки
        if self.bg:
            screen.blit(bg_img, (0, 0))
        screen.blit(self.image, self.rect)

        return ret


# иницальизирю игрока
player = Player(size_cell, screen_height - 130, int(level), int(info_dead))

# создаю группы для кажого вида спрайтов
lava_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()
score_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
dog_group = pygame.sprite.Group()

# создаю все кнопки
restart_button = Button(size_cell * 2, size_cell * 3, restart_img)
start_button = Button(size_cell * 4, size_cell * 3, start_img)
exit_button = Button(size_cell * 8, size_cell * 3, exit_img, False)
win_button = Button(screen_width // 2 - 140, size_cell * 7, exit_img, False)
new_button = Button(screen_width // 2 - 140, size_cell * 6, newGame_img, False)
stop_button = Button(screen_width - 150, screen_height - 150, stop_img, False)

# загружаю все уровни
levelLoad(8)

# загрузка мира
world = World(level_group[player.lvlUpdate() - 1])
world.reset()

# запускаю осноной цикл
run = True
while run:
    pygame.event.get()

    clock.tick(fps)

    screen.blit(bg_img, (0, 0))

    # отображаю меню
    if menu == 1:
        if start_button.draw():
            menu = 0
        if exit_button.draw():
            run = False
    # начинается игра
    else:
        world.draw()

        # вывод кнопки выхода
        if stop_button.draw():
            run = False

        # вывод всех групп спратов
        score_group.draw(screen)
        portal_group.draw(screen)
        enemy_group.update()
        enemy_group.draw(screen)

        dead = player.update(dead)
        score_ = player.ScoreUpdate()

        # проверка собраны лир все кусочки портала
        if score_ == 3:
            for item in portal_group:
                item.PortalReset()

        # вывод колличества уже собранной маны
        font = pygame.font.SysFont('Bauhaus 93', 30)
        img = font.render('Мана: ' + str(score_), True, (255, 255, 255))

        screen.blit(img, (20, 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if dead == 1:
            # если игрок погиб, то вывод кнопки
            if restart_button.draw():
                # ресетаю персонажа, мир и спрайты
                player.reset(size_cell, size_cell * 9)
                dead = 0
                ResetPortal()
                delete(enemy_group)
                delete(score_group)
                world.reset()
            if exit_button.draw():
                run = False
        else:
            # если игрок жив то вывожу все обьектына экран
            spike_group.draw(screen)
            dog_group.draw(screen)
            for i in lava_group:
                i.animation()
            for i in score_group:
                i.animation()
            lava_group.draw(screen)
            portal_group.draw(screen)
            score_group.draw(screen)
            enemy_group.draw(screen)

        # при переходе на новый уровень
        if player.lvlChange() == 1:
            # проверка не последний ли это уровень
            if player.lvlUpdate() <= len(level_group):

                # сохраение достижений и статистики
                cfg_file = open('cfg.txt', 'w')
                cfg_file.write(
                    str(player.lvlUpdate()) + ';' + str(player.deadInfo()))
                cfg_file.close()

                world_data = []
                world = new_level(level_group[player.lvlUpdate() - 1])
                dead = 0
                delete(enemy_group)
                delete(score_group)
                world.reset()
                newLevel_sfx.play()
            # если послежний то поздравляем и выводим статистику
            else:
                screen.blit(bg_img, (0, 0))
                font = pygame.font.SysFont('Bauhaus 93', 60)
                img = font.render('YOU WIN!!', True, (255, 255, 255))
                with open('cfg.txt', "r") as cfg_file:
                    cfg = cfg_file.readline()
                    cfg = cfg.split(';')

                img2 = font.render(f'Вы погибли: {cfg[1]} раз за всю игру',
                                   True, (255, 255, 255))
                screen.blit(img,
                            ((screen_width // 2) - 140, screen_height // 2))
                screen.blit(img2, (
                (screen_width // 2) - 140, screen_height // 2 + 125))
                if win_button.draw():
                    run = False
                if new_button.draw():
                    with open('cfg.txt', "w") as cfg_file:
                        cfg_file.write(str(1) + ';' + str(0))
                        cfg_file.close()
                        delete(dog_group)

                        world_data = []
                        world = new_level(level_group[0])
                        dead = 0
                        delete(enemy_group)
                        delete(score_group)
                        world.reset()
                        newLevel_sfx.play()

    pygame.display.update()

pygame.quit()
