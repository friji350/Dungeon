import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

#размер окна
screen_width = 1200
screen_height = 1000

#размер квадрата
size_cell = 100
dead = 0

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

#загрузка заднего фона
bg_img = pygame.image.load('img/background.jpg')

restart_img = pygame.image.load('img/start.png')

level_group = []

def delete(group):
	group.empty()

def levelLoad(maxLevel):
	for i in range(1,maxLevel+1):
		level_group.append(eval('lvl' + str(i)))

def new_level(lvl):
	player.reset(100, screen_height - 130)
	lava_group.empty()
	portal_group.empty()

	world = World(lvl)
	return world


class Player():
	def __init__(self, x, y):
		#списки с разными положениями персонажа во время анимации
		self.hero_r = []
		self.hero_l = []
		#загрузка тайтлов анимации
		for i in range(1, 8):
			#оригинал
			hero_l = pygame.image.load(f'img/slime{i}.png')
			#изменение размеров
			hero_l = pygame.transform.scale(hero_l, (90, 67))
			#отражаю 
			hero_r = pygame.transform.flip(hero_l, True, False)
			self.hero_r.append(hero_r)
			self.hero_l.append(hero_l)
		#кадр в анимации (0 - стоит)
		self.index = 0
		self.coun = 0
		self.jump_num = 0
		
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

		self.level = 1
		self.levelChange = 0

	def update(self, dead):
		dx = 0
		dy = 0
		#обработка нажатия клавишь
		if dead != 1:
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False and self.jump_num < 2:
				
				self.vel_y = -15
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

			
			#столкновение с блоками
			for tile in world.tile_list:
				#столкновение по "х"
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.wid, self.heig):
					dx = 0
				#столкновение по "у"
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.wid, self.heig):
					self.jump_num = 0
					#в прижке
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
						
					#падает
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						


			#столкновение с лавой
			if pygame.sprite.spritecollide(self, lava_group, False):
				dead = 1
			if pygame.sprite.spritecollide(self, spike_group, False):
				dead = 1
			if pygame.sprite.spritecollide(self, score_group, True):
				self.score += 1
			if pygame.sprite.spritecollide(self, portal_group, False):
				for i in portal_group:
					if i.PortalMode() == 1:
						self.level += 1
						self.levelChange = 1
					

			#изменение координат персонажа
			self.rect.x += dx
			self.rect.y += dy
		
		else:
			self.image = pygame.transform.scale(pygame.image.load('img/dead.png'), (100, 100))


		#не дает персанажу выпасть за пределы мира
		if self.rect.bottom > screen_height:
			self.rect.bottom = screen_height
			dy = 0

		
		screen.blit(self.image, self.rect)

		return dead
	
	def reset(self, x, y):
		#списки с разными положениями персонажа во время анимации
		self.hero_r = []
		self.hero_l = []
		#загрузка тайтлов анимации
		for i in range(1, 8):
			#оригинал
			hero_l = pygame.image.load(f'img/slime{i}.png')
			#изменение размеров
			hero_l = pygame.transform.scale(hero_l, (90, 67))
			#отражаю 
			hero_r = pygame.transform.flip(hero_l, True, False)
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
		self.wid = self.image.get_width()
		self.heig = self.image.get_height()
		self.jumped = False
		self.direction = 0
		self.score = 0

		self.levelChange = 0

	def lvlUpdate(self):
		return self.level
	
	def lvlChange(self):
		return self.levelChange
	
	def ScoreUpdate(self):
		return self.score



class World():
	def __init__(self, data):
		self.tile_list = []

		#загрузка текстур
		self.dirt_img = pygame.image.load('img/dirt.png')
		self.dirt_fish_img = pygame.image.load('img/dirt_fish.png')
		self.grass_img = pygame.image.load('img/road.png')
		self.lava_img = pygame.image.load('img/lava.png')

		self.data = data

		#чтобы не рисовать в ручную каждую "ячейку" использу матрицу с информацией о уровне
		#позволит добавить множество разных текстур и быстро создавать уровни в игре
		row = 0
		for i in self.data:
			col = 0
			for j in i:
				# 1 - блок грязи
				if j == 1:
					#изменяю размер под заданый размер
					img = pygame.transform.scale(self.dirt_img, (size_cell, size_cell))
					#создаю rect обьект
					img_rect = img.get_rect()
					#изменяю его координаты по его положению в матрице
					img_rect.x = col * size_cell
					img_rect.y = row * size_cell
					j = (img, img_rect)
					self.tile_list.append(j)
				# 2 - блок дорожки	
				if j == 2:
					img = pygame.transform.scale(self.grass_img, (size_cell, size_cell))
					img_rect = img.get_rect()
					img_rect.x = col * size_cell
					img_rect.y = row * size_cell
					j = (img, img_rect)
					self.tile_list.append(j)
				# 3 - блок земли с рыбой		
				if j == 3:
					img = pygame.transform.scale(self.dirt_fish_img, (size_cell, size_cell))
					img_rect = img.get_rect()
					img_rect.x = col * size_cell
					img_rect.y = row * size_cell
					j = (img, img_rect)
					self.tile_list.append(j)
				# 4 - лава	
				if j == 4:
					lava = LavaBlock(col * size_cell, row * size_cell + (size_cell // 4))
					lava_group.add(lava)
				#5 - шипы
				if j == 5:
					spike = SpikeBlock(col * size_cell, row * size_cell )
					spike_group.add(spike)
				#9 - портал
				if j == 9:
					portal = PortalBlock(col * size_cell, row * size_cell )
					portal_group.add(portal)
				col += 1
			row += 1


	def reset(self):
		row = 0
		for i in self.data:
			col = 0
			for j in i:
				#6 - мана
				if j == 7:
					mana = ManaBlock(col * size_cell, row * size_cell )
					score_group.add(mana)
				col += 1
			row += 1


	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
	

class LavaBlock(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/lava.png')
		self.image = pygame.transform.scale(img, (size_cell, size_cell))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

class SpikeBlock(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/spike_active.png')
		self.image = pygame.transform.scale(img, (size_cell, size_cell+40))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y-40

class PortalBlock(pygame.sprite.Sprite):
	def __init__(self, x, y):
		self.mode = 0
		self.x = x
		self.y = y
		self.mode = 0
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/portal_dis.png')
		self.image = pygame.transform.scale(img, (size_cell, size_cell+40))
		self.rect = self.image.get_rect()
		self.rect.x = self.x
		self.rect.y = self.y-40
	
	def PortalReset(self):
		self.mode = 1
		portal_group.empty()
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/portal_active.png')
		self.image = pygame.transform.scale(img, (size_cell, size_cell+40))
		self.rect = self.image.get_rect()
		self.rect.x = self.x
		self.rect.y = self.y-40
		portal_group.add(self)
	
	def PortalMode(self):
		return self.mode


class ManaBlock(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/mana.png')
		self.image = pygame.transform.scale(img, (size_cell//5, size_cell//2))
		self.rect = self.image.get_rect()
		self.rect.x = x+25
		self.rect.y = y+25



class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.push = False

	def draw(self):
		ret = False

		#позиция мышки
		pos = pygame.mouse.get_pos()

		#нажатии мышки
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.push == False:
				ret = True
				self.push = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.push = False


		#отрисовка кнопки
		screen.blit(bg_img, (0, 0))
		screen.blit(self.image, self.rect)
		

		return ret

lvl1 = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 9, 1, 1, 1], 
[1, 0, 0, 0, 2, 2, 2, 2, 2, 1, 1, 1], 
[1, 7, 0, 2, 7, 0, 0, 0, 0, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
[1, 5, 2, 2, 2, 5, 2, 0, 0, 1, 1, 1],  
[1, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1], 
[1, 0, 0, 0, 0, 7, 0, 0, 0, 1, 1, 1], 
[1, 2, 2, 2, 4, 4, 4, 2, 4, 1, 1, 1], 
[1, 3, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1]
]


lvl2 = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1]
]


player = Player(100, screen_height - 130)

lava_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()
score_group = pygame.sprite.Group()

world = World(lvl1)
world.reset()
restart_button = Button(300, 300, restart_img)


levelLoad(2)

run = True
while run:

	clock.tick(fps)

	screen.blit(bg_img, (0, 0))

	world.draw()


	score_group.draw(screen)
	portal_group.draw(screen)

	dead = player.update(dead)
	score_ = player.ScoreUpdate()
	
	if score_ == 3:
		for item in portal_group:
			item.PortalReset()

	font = pygame.font.SysFont('Bauhaus 93', 30)
	img = font.render('Мана: ' + str(score_), True, (255, 255, 255))

	screen.blit(img, (20, 20))
	

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False


	if dead == 1:
		if restart_button.draw():
			player.reset(100, screen_height - 130)
			dead = 0

			world.reset()
	else:
		spike_group.draw(screen)
		lava_group.draw(screen)
		portal_group.draw(screen)
		score_group.draw(screen)
	
	if player.lvlChange() == 1:
		world_data = []
		world = new_level(level_group[player.lvlUpdate()-1])
		dead = 0
	pygame.display.update()

pygame.quit()
