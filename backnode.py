import pygame, sys
from random import choice

#initialise pygame and game window
pygame.init()
WIDTH, HEIGHT = 1440, 810
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BACKNODE")
clock = pygame.time.Clock()

#define colours
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
DARK_GREY = (64, 64, 64)

#import tile images
img_tile_0 = pygame.transform.scale_by(pygame.image.load("pics\\tile_0.png"), 4).convert_alpha()
img_tile_0_1 = pygame.transform.scale_by(pygame.image.load("pics\\tile_0_1.png"), 4).convert_alpha()
img_tile_0_1_2 = pygame.transform.scale_by(pygame.image.load("pics\\tile_0_1_2.png"), 4).convert_alpha()
img_tile_0_1_2_3 = pygame.transform.scale_by(pygame.image.load("pics\\tile_0_1_2_3.png"), 4).convert_alpha()
img_tile_0_2 = pygame.transform.scale_by(pygame.image.load("pics\\tile_0_2.png"), 4).convert_alpha()
img_tile_01 = pygame.transform.scale_by(pygame.image.load("pics\\tile_01.png"), 4).convert_alpha()
img_tile_01_23 = pygame.transform.scale_by(pygame.image.load("pics\\tile_01_23.png"), 4).convert_alpha()
img_tile_02 = pygame.transform.scale_by(pygame.image.load("pics\\tile_02.png"), 4).convert_alpha()
img_tile_012 = pygame.transform.scale_by(pygame.image.load("pics\\tile_012.png"), 4).convert_alpha()
img_tile_0123 = pygame.transform.scale_by(pygame.image.load("pics\\tile_0123.png"), 4).convert_alpha()
img_tile_backnode = pygame.transform.scale_by(pygame.image.load("pics\\tile_backnode.png"), 4).convert_alpha()

#import token images
img_token_red = pygame.transform.scale_by(pygame.image.load("pics\\token_red.png"), 4).convert_alpha()
img_token_blue = pygame.transform.scale_by(pygame.image.load("pics\\token_blue.png"), 4).convert_alpha()

#set up array for current grid of tiles
TILELENGTH = 100
grid = list([None]*7 for x in range(7))

#set up tile hitboxes and states
for x in range(7):
    for y in range(7):
        grid[y][x] = [pygame.Rect(110*x+10, 110*y+10, TILELENGTH, TILELENGTH), None]

#set up array for all possible tiles
tiles = {
    "t0":img_tile_0,
    "t1":pygame.transform.rotate(img_tile_0, -90),
    "t2":pygame.transform.rotate(img_tile_0, 180),
    "t3":pygame.transform.rotate(img_tile_0, 90),
    "t0_1":img_tile_0_1,
    "t1_2":pygame.transform.rotate(img_tile_0_1, -90),
    "t2_3":pygame.transform.rotate(img_tile_0_1, 180),
    "t3_0":pygame.transform.rotate(img_tile_0_1, 90),
    "t0_1_2":img_tile_0_1_2,
    "t1_2_3":pygame.transform.rotate(img_tile_0_1_2, -90),
    "t2_3_0":pygame.transform.rotate(img_tile_0_1_2, 180),
    "t3_0_1":pygame.transform.rotate(img_tile_0_1_2, 90),
    "t0_1_2_3":img_tile_0_1_2_3,
    "t0_2":img_tile_0_2,
    "t1_3":pygame.transform.rotate(img_tile_0_2, -90),
    "t01":img_tile_01,
    "t12":pygame.transform.rotate(img_tile_01, -90),
    "t23":pygame.transform.rotate(img_tile_01, 180),
    "t30":pygame.transform.rotate(img_tile_01, 90),
    "t01_23":img_tile_01_23,
    "t12_30":pygame.transform.rotate(img_tile_01_23, -90),
    "t02":img_tile_02,
    "t13":pygame.transform.rotate(img_tile_02, -90),
    "t012":img_tile_012,
    "t123":pygame.transform.rotate(img_tile_012, -90),
    "t230":pygame.transform.rotate(img_tile_012, 180),
    "t301":pygame.transform.rotate(img_tile_012, 90),
    "t0123":img_tile_0123
}

#array to store position of all tokens
#each element in the array is in the form [<0 if player's token, 1 if opponent's token>, [x,y] of token, [x,y] of tile token is in, direction in tile of wire token is on]
tokens = []

### FUNCTIONS ###
def check_connected(tile, dir1, dir2):
    '''Checks if dir1 is connected to dir2 in tile'''
    dir1, dir2 = str(dir1), str(dir2)
    for x in range(len(tile)-1):
        if dir1 in tile[x:x+2] and dir2 in tile[x:x+2]:
            return True
    for x in range(len(tile)-2):
        if dir1 in tile[x:x+3] and dir2 in tile[x:x+3] and not "_" in tile[x:x+3]:
            return True
    for x in range(len(tile)-3):
        if dir1 in tile[x:x+4] and dir2 in tile[x:x+4] and not "_" in tile[x:x+4]:
            return True
    return False

DIRECTIONS = {
    0:(0,-1),
    1:(1,0),
    2:(0,1),
    3:(-1,0)
}

def is_token_valid(x, y, direction):
    tile = grid[y][x]
    if tile[1] == None:
        return False
    if not str(direction) in tile[1]:
        return False
    if wire_has_token(x, y, direction):
        return False
    return True

def wire_has_token(start_x, start_y, direction):
    '''Checks if the wire connected to the given line segment has a token on it'''
    visited = set()
    stack = [(start_x, start_y, direction)]

    while stack:
        x, y, direction = stack.pop()
        if (x,y,direction) in visited:
            continue
        visited.add((x,y,direction))

        for token in tokens:
            if token[2] == [x,y] and token[3] == direction:
                return True

        stack.append((x+DIRECTIONS[direction][0], y+DIRECTIONS[direction][1], (direction+2)%4))

        dirs = [0,1,2,3]
        dirs.pop(direction)
        for newdir in dirs:
            if grid[y][x][1] != None and check_connected(grid[y][x][1], direction, newdir):
                stack.append((x,y,newdir))

    return False


curr_tile = "t0_1_2_3"
curr_tile_rect = pygame.Rect(890, 120, TILELENGTH, TILELENGTH)

#main game loop
isRunning = True
while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #check if left click
            #check for collisions with tiles
            for x in range(7):
                for y in range(7):
                    if grid[y][x][0].collidepoint(event.pos):
                        if grid[y][x][1] == None: #collided tile is empty
                            #check if tile can be placed
                            valid = True
                            if "0" in curr_tile:
                                if y == 0:
                                    valid = False
                                elif grid[y-1][x][1] != None and not "2" in grid[y-1][x][1]:
                                    valid = False
                            else:
                                if y > 0 and grid[y-1][x][1] != None and "2" in grid[y-1][x][1]:
                                    valid = False
                                    
                            if "1" in curr_tile:
                                if x == 6:
                                    valid = False
                                elif grid[y][x+1][1] != None and not "3" in grid[y][x+1][1]:
                                    valid = False
                            else:
                                if x < 6 and grid[y][x+1][1] != None and "3" in grid[y][x+1][1]:
                                    valid = False
                                    
                            if "2" in curr_tile:
                                if y == 6:
                                    valid = False
                                elif grid[y+1][x][1] != None and not "0" in grid[y+1][x][1]:
                                    valid = False
                            else:
                                if y < 6 and grid[y+1][x][1] != None and "0" in grid[y+1][x][1]:
                                    valid = False
                                    
                            if "3" in curr_tile:
                                if x == 0:
                                    valid = False
                                elif grid[y][x-1][1] != None and not "1" in grid[y][x-1][1]:
                                    valid = False
                            else:
                                if x > 0 and grid[y][x-1][1] != None and "1" in grid[y][x-1][1]:
                                    valid = False

                            if valid:
                                grid[y][x][1] = curr_tile
                                curr_tile = choice(list(tiles.keys()))
                                
                        else: #collided tile is occupied
                            #check to which side it's closest to
                            updist = event.pos[1]-grid[y][x][0].y
                            downdist = TILELENGTH+grid[y][x][0].y-event.pos[1]
                            leftdist = event.pos[0]-grid[y][x][0].x
                            rightdist = TILELENGTH+grid[y][x][0].x-event.pos[0]

                            closest = min(updist, downdist, leftdist, rightdist)
                            if closest == updist:
                                if is_token_valid(x,y,0):
                                    tokens.append([0, event.pos, [x,y], 0])
                            elif closest == rightdist:
                                if is_token_valid(x,y,1):
                                    tokens.append([0, event.pos, [x,y], 1])
                            elif closest == downdist:
                                if is_token_valid(x,y,2):
                                    tokens.append([0, event.pos, [x,y], 2])
                            else:
                                if is_token_valid(x,y,3):
                                    tokens.append([0, event.pos, [x,y], 3])

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r or event.key == pygame.K_SPACE: #rotate key pressed
                if curr_tile == "t1_3":
                    curr_tile = "t0_2"
                elif curr_tile == "t13":
                    curr_tile = "t02"
                elif not ("1" in curr_tile and "2" in curr_tile and "3" in curr_tile and "0" in curr_tile):
                    curr_tile = curr_tile.translate(str.maketrans("0123", "1230"))
                elif curr_tile == "t01_23":
                    curr_tile = "t12_30"
                elif curr_tile == "t12_30":
                    curr_tile = "t01_23"

    #draw screen and tiles
    screen.fill(BLACK)
    for row in grid:
        for tile in row:
            if tile[1]:
                screen.blit(tiles[tile[1]], tile[0])
            else:
                pygame.draw.rect(screen, DARK_GREY, tile[0])

    screen.blit(tiles[curr_tile], curr_tile_rect)

    #draw tokens
    for token in tokens:
        screen.blit(img_token_blue if token[0] == 0 else img_token_red, pygame.Rect(token[1][0]-20, token[1][1]-20, 40, 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
