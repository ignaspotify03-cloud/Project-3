import pygame, sys

def dispStory(story_path):
    #initialise pygame
    pygame.init()
    WIDTH, HEIGHT = 1440, 810
    FPS, SCROLLSPEED = 60, 5
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Courier New", 24, bold = True)
    header_font = pygame.font.SysFont("Courier New", 28, bold = True)

    #dialogue box setup
    box_width, box_height = int(WIDTH*0.9), int(HEIGHT*0.3)
    text_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA) #SRCALPHA enables per-pixel alpha, allowing each pixel to have its own alpha value
    text_surf.fill((0,0,0,200))

    story = []
    with open(story_path, 'r') as file:
        story = file.readlines()

    start_time = pygame.time.get_ticks()
    isRunning = True
    while isRunning:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if len(story) != 0:
                    story.pop(0)
                    start_time = pygame.time.get_ticks()

        #display text
        if len(story) == 0:
            isRunning = False
        else:
            elapsed_timems = pygame.time.get_ticks() - start_time
            text_progress = min(1, elapsed_timems/1000*SCROLLSPEED)
            text_surf.fill((0,0,0,200))
            img, header, text = story[0].strip().split('|')
            if img:
                #change person talking on screen
                pass
            header_render = header_font.render(header, True, (255, 220, 100))
            text_render = font.render(text[:int(len(text)*text_progress)], True, (255, 255, 255))

            # Blit onto dialogue surface
            text_surf.blit(header_render, (20, 15))
            text_surf.blit(text_render, (20, 55))
        
        screen.fill((64, 64, 64))
        screen.blit(text_surf, (WIDTH*0.05, HEIGHT*0.65))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
