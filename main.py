import pygame, sys
from random import random
import battle
import models
import dialogue

#initialise pygame
pygame.init()
WIDTH, HEIGHT = 1440, 810
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Project 3")
clock = pygame.time.Clock()

menu_font = pygame.font.SysFont("Courier_New", 48, bold = True)

#menu buttons setup
play_surf = pygame.Surface((int(WIDTH*0.5), int(HEIGHT*0.1)), pygame.SRCALPHA)
play_surf.fill((0, 0, 0, 200))
play_render = menu_font.render("PLAY", True, (255,255,255))
text_rect = play_render.get_rect(center=play_surf.get_rect().center) #centre text to surface
play_surf.blit(play_render, text_rect)
play_rect = play_surf.get_rect()
play_rect.topleft = (int(WIDTH*0.25), int(HEIGHT*0.5))

settings_surf = pygame.Surface((int(WIDTH*0.5), int(HEIGHT*0.1)), pygame.SRCALPHA)
settings_surf.fill((0, 0, 0, 200))
settings_render = menu_font.render("SETTINGS", True, (255,255,255))
text_rect = settings_render.get_rect(center=settings_surf.get_rect().center)
settings_surf.blit(settings_render, text_rect)
settings_rect = settings_surf.get_rect()
settings_rect.topleft = (int(WIDTH*0.25), int(HEIGHT*0.65))

exit_surf = pygame.Surface((int(WIDTH*0.5), int(HEIGHT*0.1)), pygame.SRCALPHA)
exit_surf.fill((0, 0, 0, 200))
exit_render = menu_font.render("EXIT", True, (255,255,255))
text_rect = exit_render.get_rect(center=exit_surf.get_rect().center)
exit_surf.blit(exit_render, text_rect)
exit_rect = exit_surf.get_rect()
exit_rect.topleft = (int(WIDTH*0.25), int(HEIGHT*0.8))

screen.fill((64,64,64))
screen.blit(play_surf, (int(WIDTH*0.25), int(HEIGHT*0.5)))
screen.blit(settings_surf, (int(WIDTH*0.25), int(HEIGHT*0.65)))
screen.blit(exit_surf, (int(WIDTH*0.25), int(HEIGHT*0.8)))

pygame.display.flip()

#main menu loop
isMenu, isPlaying = True, False
while isMenu:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isMenu = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_rect.collidepoint(event.pos):
                isMenu, isPlaying = False, True
            elif settings_rect.collidepoint(event.pos):
                pass
            elif exit_rect.collidepoint(event.pos):
                isMenu = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

#game loop
if isPlaying:
    dialogue.dispStory('text\story\intro.txt')
    
    Player = models.Player(Name = "Player", hp = 20, ep = 10, df = 2, atk = 5, lk = 5)
    Ramburger = models.Item(Name = "R.A.M.Burger", effects = [["hp", False, 20, "hp_max"]], useText = "ate the R.A.M.Burger")
    Player.GainItem(Ramburger, 5)

    Rock = models.Tool(Name = "Rocks", cost = 2, effects = [[models.DAMAGE, 5]], desc = "Does 5 damage")
    DEVSTICK = models.Tool(Name = "DEVSTICK", cost = 0, effects = [[models.ELEC_DAMAGE, 99]], desc = "Does 99 electrical damage")
    Player.GainTool(Rock)
    Player.GainTool(DEVSTICK)

    img, colour, enemies = battle.SetUpBattle("Street", 7)       
    battle.StartBattle("Street", Player, enemies)

sys.exit()
