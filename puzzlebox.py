import pygame, sys

#initialise pygame and game window
pygame.init()
WIDTH, HEIGHT = 1030, 810
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PUZZLEBOX")
clock = pygame.time.Clock()

WaitOneSec = pygame.USEREVENT + 1

#define colours
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_GREY = (64, 64, 64)

#import button type images
img_dot_b = pygame.transform.scale_by(pygame.image.load("pics\dot_b.png"), 10).convert_alpha()
img_dot_w = pygame.transform.scale_by(pygame.image.load("pics\dot_w.png"), 10).convert_alpha()
img_arrow_r = pygame.transform.scale_by(pygame.image.load("pics\\arrow_r.png"), 10).convert_alpha()
img_arrow_dr = pygame.transform.scale_by(pygame.image.load("pics\\arrow_dr.png"), 10).convert_alpha()
img_mouth_r = pygame.transform.scale_by(pygame.image.load("pics\mouth_r.png"), 10).convert_alpha()
img_mouth_dr = pygame.transform.scale_by(pygame.image.load("pics\mouth_dr.png"), 10).convert_alpha()


#button hitbox setup
b1, b2, b3 = pygame.Rect(10, 10, 250, 250), pygame.Rect(280, 10, 250, 250), pygame.Rect(550, 10, 250, 250)
b4, b5, b6 = pygame.Rect(10, 280, 250, 250), pygame.Rect(280, 280, 250, 250), pygame.Rect(550, 280, 250, 250)
b7, b8, b9 = pygame.Rect(10, 550, 250, 250), pygame.Rect(280, 550, 250, 250), pygame.Rect(550, 550, 250, 250)
submit = pygame.Rect(820, 10, 200, 790)

#button dict for easy access
buttons = {
    1:b1, 2:b2, 3:b3,
    4:b4, 5:b5, 6:b6,
    7:b7, 8:b8, 9:b9
}

#button state table
states = [[False, False, False],
          [False, False, False],
          [False, False, False]]

#button type table
types = [["dot_b", "arrow_dl", "mouth_d"],
         ["dot_w", "dot_b", "dot_b"],
         ["mouth_ur", "arrow_u", "dot_w"]]

#button type image dict
type_images = {
    "dot_b":img_dot_b,
    "dot_w":img_dot_w,
    "arrow_r":img_arrow_r,
    "arrow_dr":img_arrow_dr,
    "arrow_d":pygame.transform.rotate(img_arrow_r, -90),
    "arrow_dl":pygame.transform.rotate(img_arrow_dr, -90),
    "arrow_l":pygame.transform.rotate(img_arrow_r, 180),
    "arrow_ul":pygame.transform.rotate(img_arrow_dr, 180),
    "arrow_u":pygame.transform.rotate(img_arrow_r, 90),
    "arrow_ur":pygame.transform.rotate(img_arrow_dr, 90),
    "mouth_r":img_mouth_r,
    "mouth_dr":img_mouth_dr,
    "mouth_d":pygame.transform.rotate(img_mouth_r, -90),
    "mouth_dl":pygame.transform.rotate(img_mouth_dr, -90),
    "mouth_l":pygame.transform.rotate(img_mouth_r, 180),
    "mouth_ul":pygame.transform.rotate(img_mouth_dr, 180),
    "mouth_u":pygame.transform.rotate(img_mouth_r, 90),
    "mouth_ur":pygame.transform.rotate(img_mouth_dr, 90)
}

gameState = 0

#main game loop
isRunning = True
while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

        #detect left mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #Left mouse click
                #check for collision with buttons
                for x in range(3):
                    for y in range(3):
                        if buttons[y+3*x+1].collidepoint(event.pos):
                            states[x][y] = not(states[x][y])

                if submit.collidepoint(event.pos): #submit button clicked while clickable
                    pygame.time.set_timer(WaitOneSec, 1000, loops=1) #set a 1 sec timer where button will not be clickable
                    #check if all button types have been satisfied (gameState=1) or not (gameState=-1)
                    gameState = 1
                    for x in range(3):
                        for y in range(3):
                            if types[x][y] and gameState != -1:
                                if types[x][y] == "dot_b" and states[x][y] == True:
                                    gameState = -1
                                    break
                                if types[x][y] == "dot_w" and states[x][y] == False:
                                    gameState = -1
                                    break

                                targ_x, targ_y = None, None
                                if "_dr" in types[x][y] and x<2 and y<2:
                                    targ_x, targ_y = x+1, y+1
                                elif "_dl" in types[x][y] and x<2 and y>0:
                                    targ_x, targ_y = x+1, y-1
                                elif "_ur" in types[x][y] and x>0 and y<2:
                                    targ_x, targ_y = x-1, y+1
                                elif "_ul" in types[x][y] and x>0 and y>0:
                                    targ_x, targ_y = x-1, y-1
                                elif "_d" in types[x][y] and x<2:
                                    targ_x, targ_y = x+1, y
                                elif "_r" in types[x][y] and y<2:
                                    targ_x, targ_y = x, y+1
                                elif "_u" in types[x][y] and x>0:
                                    targ_x, targ_y = x-1, y
                                elif "_l" in types[x][y] and y>0:
                                    targ_x, targ_y = x, y-1
                                    
                                if "arrow_" in types[x][y] and targ_x != None and targ_y != None and states[targ_x][targ_y] != states[x][y]:
                                    gameState = -1
                                    break
                                elif "mouth_" in types[x][y] and targ_x != None and targ_y != None and states[targ_x][targ_y] == states[x][y]:
                                    gameState = -1
                                    break

        elif event.type == WaitOneSec: #1 minute is up
            gameState = 0
                
    #draw screen and buttons
    screen.fill(BLACK)
    if gameState == 0:
        for x in range(3):
            for y in range(3):
                pygame.draw.rect(screen, BLUE if states[x][y] else DARK_GREY, buttons[y+3*x+1])
    else:
        for x in range(3):
            for y in range(3):
                pygame.draw.rect(screen, RED if gameState == -1 else GREEN, buttons[y+3*x+1])
    
    pygame.draw.rect(screen, DARK_GREY if gameState == 0 else GREEN, submit)
    

    #draw button types
    for x in range(3):
        for y in range(3):
            if types[x][y] in type_images.keys():
                img_rect = type_images[types[x][y]].get_rect()
                img_rect.center = buttons[y+3*x+1].center
                screen.blit(type_images[types[x][y]], img_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

