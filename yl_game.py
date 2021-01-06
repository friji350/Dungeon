import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

#размер окна
screen_width = 1000
screen_height = 1000

#размер квадрата
size_cell = 100

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

#загрузка заднего фона
bg_img = pygame.image.load('img/background.jpg')


class Player():
	def __init__(self, x, y):
		#списки с разными положениями персонажа во время анимации
		self.hero_r = []
		self.hero_l = []
		#загрузка тайтлов анимации
		for i in range(1, 5):
			#оригинал
			hero_r = pygame.image.load(f'img/guy{i}.png')
			#изменение размеров
			hero_r = pygame.transform.scale(hero_r, (100, 100))
			#отражаю 
			hero_l = pygame.transform.flip(hero_r, True, False)
			self.hero_r.append(hero_r)
			self.hero_l.append(hero_l)
		#кадр в анимации (0 - стоит)
		self.index = 0
		self.coun = 0
		
		self.image = self.hero_r[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.vel_y = 0
		self.jumped = False
		self.direction = 0

	def update(self):
		dx = 0
		dy = 0
		#обработка нажатия клавишь
		key = pygame.key.get_pressed()
		if key[pygame.K_SPACE] and self.jumped == False:
			self.vel_y = -15
			self.jumped = True
		if key[pygame.K_SPACE] == False:
			self.jumped = False
		if key[pygame.K_LEFT]:
			dx -= 5
			self.coun += 1
			self.direction = -1
		if key[pygame.K_RIGHT]:
			dx += 5
			self.coun += 1
			self.direction = 1
		if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
			self.coun = 0
			self.index = 0
			if self.direction == 1:
				self.image = self.hero_r[self.index]
			if self.direction == -1:
				self.image = self.hero_l[self.index]


		#обработка анимации
		if self.coun > 5:
			self.coun = 0	
			self.index += 1
			if self.index >= len(self.hero_r):
				self.index = 0
			if self.direction == 1:
				self.image = self.hero_r[self.index]
			if self.direction == -1:
				self.image = self.hero_l[self.index]


		#"гравтация"
		#коэффициент высоты прыжка
		coefficient_gravity = 1
		#скорость падения
		speed_fall = 10
		self.vel_y += coefficient_gravity
		if self.vel_y > speed_fall:
			self.vel_y = speed_fall
		dy += self.vel_y


		#изменение координат персонажа
		self.rect.x += dx
		self.rect.y += dy

		#не дает персанажу выпасть за пределы мира
		if self.rect.bottom > screen_height:
			self.rect.bottom = screen_height
			dy = 0

		
		screen.blit(self.image, self.rect)




class World():
	def __init__(self, data):
		self.tile_list = []

		#загрузка текстур
		dirt_img = pygame.image.load('img/dirt.png')
		dirt_fish_img = pygame.image.load('img/dirt_fish.png')
		grass_img = pygame.image.load('img/grass.png')
		lava_img = pygame.image.load('img/lava.png')

		#чтобы не рисовать в ручную каждую "ячейку" использу матрицу с информацией о уровне
		#позволит добавить множество разных текстур и быстро создавать уровни в игре
		row = 0
		for i in data:
			col = 0
			for j in i:
				# 1 - блок грязи
				if j == 1:
					#изменяю размер под заданый размер
					img = pygame.transform.scale(dirt_img, (size_cell, size_cell))
					#создаю rect обьект
					img_rect = img.get_rect()
					#изменяю его координаты по его положению в матрице
					img_rect.x = col * size_cell
					img_rect.y = row * size_cell
					j = (img, img_rect)
					self.tile_list.append(j)
				# 2 - блок дорожки	
				if j == 2:
					img = pygame.transform.scale(grass_img, (size_cell, size_cell))
					img_rect = img.get_rect()
					img_rect.x = col * size_cell
					img_rect.y = row * size_cell
					j = (img, img_rect)
					self.tile_list.append(j)
				# 3 - блок земли с рыбой		
				if j == 3:
					img = pygame.transform.scale(dirt_fish_img, (size_cell, size_cell))
					img_rect = img.get_rect()
					img_rect.x = col * size_cell
					img_rect.y = row * size_cell
					j = (img, img_rect)
					self.tile_list.append(j)
				# 3 - лава	
				if j == 4:
					img = pygame.transform.scale(lava_img, (size_cell, size_cell))
					img_rect = img.get_rect()
					img_rect.x = col * size_cell
					img_rect.y = row * size_cell
					j = (img, img_rect)
					self.tile_list.append(j)
				col += 1
			row += 1

	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])



world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 1],  
[1, 0, 0, 0, 0, 2, 4, 4, 4, 1], 
[1, 2, 2, 2, 2, 2, 1, 1, 1, 1], 
[1, 2, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 1, 1, 1, 1, 1, 3, 1, 3, 1]
]



player = Player(100, screen_height - 130)
world = World(world_data)

run = True
while run:

	clock.tick(fps)

	screen.blit(bg_img, (0, 0))

	world.draw()

	player.update()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()
