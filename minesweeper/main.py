import pygame, random, math

from pygame.locals import *
pygame.init()

WIDTH, HEIGHT = 600, 650

screen = pygame.display.set_mode((WIDTH, HEIGHT))

is_running = True

background = pygame.image.load("background.png").convert()


class Tile:
    size = 30
    flag = pygame.image.load("faces/flag.png")
    font = pygame.font.Font("SourceSansPro-Bold.ttf", 24)

    def __init__(self, x, y):
        self.d = pygame.Vector2(x, y)
        self.flagged = False
        self.hidden = True
        self.is_bomb = False
        self.num_surrouding_bombs = 0

    def draw(self, screen, number):
        if self.flagged:
            screen.blit(self.flag, (self.d.x*self.size, self.d.y*self.size))
        elif not self.hidden:
            if self.is_bomb:
                screen.blit(pygame.image.load("faces/bomb.png"), (self.d.x*self.size, self.d.y*self.size))
            elif not number == 0:
                screen.blit(pygame.image.load("faces/-1.png"), (self.d.x*self.size, self.d.y*self.size))

                if number != -1:
                    t = self.font.render(str(number), True, (0,0,0))
                    screen.blit(t, ((self.d.x + 0.5)*self.size - t.get_width()/2, (self.d.y + 0.5)*self.size - t.get_height()/2))

class Clock:
    font = pygame.font.Font("SourceSansPro-Bold.ttf", 40)

    def __init__(self):
        self.minutes = 0
        self.seconds = 0
        self.text = ""

    def update(self, difference):
        self.total = pygame.time.get_ticks()/1000 - difference #total ticks since program first ran - the duration

        self.minutes = int(self.total / 60)
        self.seconds = int(self.total % 60)

    def draw(self, screen):
        self.text = self.font.render(str(self.minutes) + ":" + ("0" if self.seconds < 10 else "") + str(self.seconds), True, (0,0,0))
        screen.blit(self.text, (300 - self.text.get_width()/2, 625 - self.text.get_height()/2))




class Game:
    total_bombs = 30

    sa = -0.0005 #menu acceleration
    font_end = pygame.font.Font("SourceSansPro-Regular.ttf", 100)
    text = ""

    def __init__(self, size, pressing = False):
        self.dim = size
        self.tiles = []
        self.pressing = pressing
        self.gameover = 0
        self.end_screen = False

        self.s = pygame.Rect(0, 680, 600, 650)
        self.sv = 0

        self.score = 0
        self.time_diff = pygame.time.get_ticks()/1000
        self.counter = Clock()

        for i in range(self.dim ** 2):
            y = int(i/self.dim)
            x = int(i%self.dim)
            self.tiles.append(Tile(x, y))
        
        self.spread_bombs()
        self.calculate_values()

    def spread_bombs(self):
        #spreading the bombs
        put_geese = 0
        while put_geese < self.total_bombs:
            x = random.randint(0, 19) 
            y = random.randint(0, 19)

            i = y*self.dim + x

            if self.tiles[i].is_bomb == False:
                self.tiles[i].is_bomb = True
                self.tiles[i].num_surrounding_bombs = 9
                put_geese += 1

    def calculate_values(self):
        for tile in self.tiles:
            hug_left = False
            hug_top = False
            hug_right = False
            hug_bottom = False
            num_bombs = int(0)
            
            i = int(tile.d.y * self.dim + tile.d.x)

            if not tile.is_bomb:
                if tile.d.x == 0:
                    hug_left = True
                if tile.d.x == self.dim - 1:
                    hug_right = True
                if tile.d.y == 0:
                    hug_top = True
                if tile.d.y == self.dim - 1:
                    hug_bottom = True

                
                if not hug_top and not hug_left:
                    if self.tiles[i - self.dim - 1].is_bomb:
                        num_bombs += 1
                if not hug_top:
                    if self.tiles[i - self.dim].is_bomb:
                        num_bombs += 1
                if not hug_top and not hug_right:
                    if self.tiles[i - self.dim + 1].is_bomb:
                        num_bombs += 1

                if not hug_left:
                    if self.tiles[i - 1].is_bomb:
                        num_bombs += 1
                if not hug_right:
                    if self.tiles[i + 1].is_bomb:
                        num_bombs += 1

                if not hug_bottom and not hug_left:
                    if self.tiles[i + self.dim - 1].is_bomb:
                        num_bombs += 1
                if not hug_bottom:
                    if self.tiles[i + self.dim].is_bomb:
                        num_bombs += 1
                if not hug_bottom and not hug_right:
                    if self.tiles[i + self.dim + 1].is_bomb:
                        num_bombs += 1
                
                tile.num_surrounding_bombs = int(num_bombs)

    def flag(self, i):
        if self.tiles[i].hidden:
            self.tiles[i].flagged = not self.tiles[i].flagged

    def reveal(self, i):
        tile = self.tiles[i]

        if not tile.flagged and tile.hidden:
            tile.hidden = False
            
            if tile.is_bomb:
                self.gameover = 1

            elif tile.num_surrounding_bombs == 0:
                tile.num_surrounding_bombs = -1

                hug_left = False
                hug_top = False
                hug_right = False
                hug_bottom = False
                
                if tile.d.x == 0:
                    hug_left = True
                if tile.d.x == self.dim - 1:
                    hug_right = True
                if tile.d.y == 0:
                    hug_top = True
                if tile.d.y == self.dim - 1:
                    hug_bottom = True

                if not hug_left and not hug_top:
                    self.reveal(i - self.dim - 1)
                if not hug_top:
                    self.reveal(i - self.dim)
                if not hug_right and not hug_top:
                    self.reveal(i - self.dim + 1)
                
                if not hug_left:
                    self.reveal(i - 1)
                if not hug_right:
                    self.reveal(i + 1)

                if not hug_left and not hug_bottom:
                    self.reveal(i + self.dim - 1)
                if not hug_bottom:
                    self.reveal(i + self.dim)
                if not hug_right and not hug_bottom:
                    self.reveal(i + self.dim + 1)
            
    def check_end(self):
        flagged_bombs = 0

        for tile in self.tiles:
            if tile.is_bomb and tile.flagged:
                flagged_bombs += 1

        if flagged_bombs == self.total_bombs:
            self.gameover = 2

    def end_game(self, dt):
        text = "You lose" if self.gameover == 1 else "You win"

        self.end_message = self.font_end.render(text, True, (0,0,0))

        if self.s.top > 0:
            self.s.y += self.sv * dt
            self.sv += self.sa * dt
        else:
            self.s.top = 0
            self.end_screen = True
 
    def update(self, x, y, click, screen, dt):
        if click[0] and not self.pressing and self.gameover == 0: #left click
            self.reveal(y*self.dim + x)
            self.pressing = True

        if click[2] and not self.pressing and self.gameover == 0: #right click
            self.flag(y*self.dim + x)
            self.pressing = True

        if self.pressing and not (click[0] or click[2]):
            self.pressing = False
        
        self.check_end()


        self.counter.update(self.time_diff)

        if self.gameover != 0:
            self.score = self.counter.text if self.score == 0 else self.score
            
            if not self.end_screen:
                self.end_game(dt)
            
            if self.end_screen:
                self.time_diff = self.counter.total
                if pygame.key.get_pressed()[K_SPACE] or pygame.mouse.get_pressed()[0]:
                    self.end_screen = False
                    
                    for tile in self.tiles:
                        del tile
                    self.__init__(20, True)

    def draw(self, screen):
        if not self.end_screen:
            screen.blit(background, (0,0))
            pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(0, 600, 600, 50))
            self.counter.draw(screen)

            for tile in self.tiles:
                tile.draw(screen, tile.num_surrounding_bombs)
        
        if self.gameover != 0:
            pygame.draw.rect(screen, (255,255,255), self.s)
            screen.blit(self.end_message, (300 - self.end_message.get_width()/2, self.s.y + 200))

            screen.blit(self.score, (300 - self.score.get_width()/2, self.s.y + 250 + self.score.get_height()))
                    
g = Game(20)


pt = pygame.time.get_ticks()
while is_running:
    ct = pygame.time.get_ticks()
    dt = ct - pt 
    pt = ct

    
    mx, my = pygame.mouse.get_pos()


    g.update(int(mx/Tile.size), int(my/Tile.size), pygame.mouse.get_pressed(), screen, dt)
    g.draw(screen)
    


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

    pygame.display.update()
pygame.quit()