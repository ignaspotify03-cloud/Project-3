import pygame, sys
from random import random, randint, choices
import models

colours = {
    'RED':(255,0,0),
    'YELLOW':(255,255,0),
    'GREEN':(0,255,0),
    'BLEEN':(0,255,255),
    'BLUE':(0,0,255),
    'PURPLE':(255,0,255)
}

def GetThreat(enemyID):
    with open("text\enemies.txt", 'r') as file:
        for enemy in file:
            if enemy[0] == '#':
                continue
            enemy = enemy.strip().split('|')
            if enemy[0] == enemyID:
                return int(enemy[3])

def GetEnemy(enemyID):
    with open("text\enemies.txt", 'r') as file:
        for enemy in file:
            if enemy[0] == '#':
                continue
            enemy = enemy.strip().split('|')
            if enemy[0] == enemyID:
                Name, desc = enemy[1], enemy[4]
                stats = []
                for i in range(5,11):
                    if '~' in enemy[i]:
                        lo, hi = enemy[i].split('~')
                        stats.append(randint(int(lo), int(hi)))
                    else:
                        stats.append(int(enemy[i]))

                loot = enemy[11:]
                loot = [thing for thing in loot if thing != ""]

                SRAM = models.Item(Name = "Spare R.A.M.", effects = [["hp", False, 10, "hp_max"]], useText = "ate the spare R.A.M")
                loot = [SRAM]

                return models.Enemy(Name = Name, hp = stats[0], ep = stats[1], df = stats[2], atk = stats[3], lk = stats[4], desc = desc, xp = stats[5], loot = loot)
                

def SetUpBattle(eventName, threat):
    '''returns img, rgb colour, list of enemy objects'''
    with open("text\scenes.txt", 'r') as file:
        for scene in file:
            scene = scene.strip().split('|')
            if scene[0].lower() == eventName.lower():
                img, colour, bossID = scene[1], colours[scene[2]], scene[3]
                enemiesID = scene[4:]
                enemies = []
                #add boss first
                if bossID:
                    threat -= GetThreat(bossID)
                    enemies.append(GetEnemy(bossID))

                #add supports
                weights = []
                for enemyID in enemiesID:
                    weights.append(GetThreat(enemyID))
                while threat > 0:
                    choice = choices(enemiesID, weights)[0]
                    enemy_threat = GetThreat(choice)
                    if enemy_threat <= threat:
                        enemies.append(GetEnemy(choice))
                        threat -= enemy_threat

    return img, colour, enemies

def StartBattle(scene, player, enemies):
    '''Starts a Battle.
    Scene should be scene object, player should be entity object, enemies should be list of entity objects'''

    announcements = ["It's your turn."]

    #initialise pygame
    pygame.init()
    WIDTH, HEIGHT = 1440, 810
    FPS = 60
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Courier New", 20, bold = True)
    header_font = pygame.font.SysFont("Courier New", 24, bold = True)

    ### set up scene (backgrounds, sounds)
    pygame.display.set_caption(scene)

    #set up UI
    info_surf = pygame.Surface((300, 200), pygame.SRCALPHA)
    info_surf.fill((0, 0, 0, 200))
    text_surf = pygame.Surface((int(WIDTH*0.9), int(HEIGHT*0.3)), pygame.SRCALPHA) #SRCALPHA enables per-pixel alpha, allowing each pixel to have its own alpha value
    text_surf.fill((0,0,0,100))
    bottom_surf = pygame.Surface((int(WIDTH), 50), pygame.SRCALPHA)
    bottom_surf.fill((0,0,0,255))
    
    screen.blit(text_surf, (WIDTH*0.05, HEIGHT*0.65))

    #set up enemies and hitboxes
    HITBOXPOS = [(60,60), (340,160), (620,60), (900,160), (1180,60)]
    enemypos = [None, None, None, None, None]
    for i in range(len(enemies)):
        pos = randint(0, len(enemypos)-1)
        while enemypos[pos] != None:
            pos = randint(0, len(enemypos)-1)
        enemypos[pos] = enemies[i].Name
        enemies[i] = [pos, pygame.Rect(HITBOXPOS[pos][0], HITBOXPOS[pos][1], 200, 200), enemies[i]]
        
    #set up turn order (player has an id of 0, rest are the enemy's positions
    turnOrder = [-1] + [enemies[i][0] for i in range(len(enemies))]

    #battle loop
    isBattling = True
    battleMode = 0 #0 = player's turn/player defending, 1 = player attacking, 2 = player using item, 3 = enemy attacking, 4 = player using tool
    selectedItem = 0
    while isBattling:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isBattling = False

            elif event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_1: #if key 1 pressed:
                    if battleMode == 1:
                        battleMode = 0
                        announcements.append("Attack deselected.")
                    elif battleMode != 3: #don't let player select modes while enemies are fighting
                        battleMode = 1
                        announcements.append("Attack selected. Click on an enemy to attack.") 

                elif event.key == pygame.K_2: #if key 2 pressed:
                    if battleMode != 3:
                        announcements.append(f"You brace yourself for attacks. Defence increased by {player.Defend()} for this turn.")
                        battleMode = 3
                        turnOrder.append(turnOrder.pop(0))

                elif event.key == pygame.K_3: #if key 3 pressed:
                    if battleMode == 2:
                        selectedItem += 1
                        if selectedItem > len(player.inv):
                            selectedItem = 0
                    elif battleMode != 3:
                        battleMode = 2
                        selectedItem = 0
                elif event.key == pygame.K_4: #if key 4 pressed:
                    if battleMode == 4:
                        selectedItem += 1
                        if selectedItem > len(player.tools):
                            selectedItem = 0
                    elif battleMode != 3:
                        battleMode = 4
                        selectedItem = 0
                    
            elif event.type == pygame.MOUSEBUTTONDOWN: #if screen clicked
                if battleMode == 2: #select and use Item
                    if selectedItem == 0:
                        battleMode = 0
                    else:
                        itemName = player.GetInventory()[selectedItem-1][0]
                        item = player.RemoveItem(itemName)
                        isUsedOnEnemy = False
                        for enemy in enemies: #check if item was used on an enemy
                            if enemy[1].collidepoint(event.pos):
                                isUsedOnEnemy = True
                                output = item.UseItem(enemy[2])
                        if not isUsedOnEnemy:
                            output = item.UseItem(player)
                        for line in output.split('\n'):
                            if line:
                                announcements.append(line)
                        battleMode = 3
                        turnOrder.append(turnOrder.pop(0))

                elif battleMode == 4: #select and use Tool
                    if selectedItem == 0:
                        battleMode = 0
                    else:
                        toolName = player.GetTools()[selectedItem-1][0]
                        tool = player.UseTool(toolName)
                        if tool == False:
                            announcements.append(f"You cannot use {toolName}. Check your EP and your tool's cooldown.")
                            battleMode = 0
                        else:
                            isUsedOnEnemy = False
                            for enemy in enemies: #check if item was used on an enemy
                                if enemy[1].collidepoint(event.pos):
                                    isUsedOnEnemy = True
                                    output = tool.UseTool(player, enemy[2])
                            if not isUsedOnEnemy:
                                output = tool.UseTool(player, player)
                            for line in output.split('\n'):
                                if line:
                                    announcements.append(line)
                            battleMode = 0
                            announcements.append("It's still your turn.")
                        
                elif battleMode == 3: #progress enemy text
                    next_enemy = turnOrder.pop(0)
                    turnOrder.append(next_enemy)
                    for enemy in enemies:
                        if enemy[0] == next_enemy:
                            next_enemy = enemy[2]
                            break

                    hasCrit, rawDamage = next_enemy.DealDamage()
                    announcements.append(f"{next_enemy.Name} attacks for {rawDamage} damage.{' Critical Hit!' if hasCrit else ''}")
                    recv_damage = player.RecvDamage(rawDamage)
                    if recv_damage == False:
                        announcements.append(f"You dodged the attack!")
                    else:
                        announcements.append(f"You took {recv_damage} damage from {next_enemy.Name}.")
                            
                    if turnOrder[0] == -1:
                        battleMode = 0
                        player.GameTick()
                        for enemy in enemies:
                            enemy[2].GameTick()
                        announcements.append(f"It's your turn. What will you do?")

                else:
                    for enemy in enemies:
                        if enemy[1].collidepoint(event.pos):
                            if battleMode == 1:
                                hasCrit, rawDamage = player.DealDamage()
                                announcements.append(f"You strike at {enemy[2].Name}, attacking for {rawDamage} damage.{' Critical Hit!' if hasCrit else ''}")
                                recv_damage = enemy[2].RecvDamage(rawDamage)
                                if recv_damage == False:
                                    announcements.append(f"The {enemy[2].Name} dodged the attack!")
                                else:
                                    announcements.append(f"The {enemy[2].Name} took {recv_damage} damage.")
                                battleMode = 3
                                turnOrder.append(turnOrder.pop(0))
                            else:
                                announcements.append(enemy[2].desc)
                                pass
                    
                    ### DETECT IF MENU KEYS ARE PRESSED

        #check if enemies are dead
        for enemy in enemies:
            if enemy[2].IsDead():
                announcements.append(f"{enemy[2].Name} died!")
                xp, loot = enemy[2].dropLoot()
                announcements.append(f"{enemy[2].Name} dropped {xp} xp! {'Level Up!' if player.gainXP(xp) else ''}")
                if loot: #handle loot collection
                    for item in loot:
                        announcements.append(f"{enemy[2].Name} dropped {item.Name}!")
                        if item.type == models.TOOL:
                            player.GainTool(item)
                        elif item.type == models.ITEM:
                            player.GainItem(item)
                turnOrder.remove(enemy[0])
                enemies.remove(enemy)
                

        #draw in the order enemy > text > bottomline > infotext
        screen.fill((64,64,64))
        for enemy in enemies:
            pygame.draw.rect(screen, (255, 0, 0), enemy[1])

        text_surf.fill((0,0,0,100))

        if battleMode == 2: #print inventory
            text_render = header_font.render("INVENTORY (CLICK ON ENEMY TO USE ON ENEMY, CLICK ANYWHERE ELSE TO USE ON SELF)", True, (255,220,100) if selectedItem == 0 else (255,255,255))
            text_surf.blit(text_render, (10, 10))
            inv = player.GetInventory()
            for i in range(len(inv)):
                text_render = font.render(f"{inv[i][0]:<20}{inv[i][1]}", True, (255,255,255) if i != (selectedItem-1) else (255,220,100))
                text_surf.blit(text_render, (12, 40+(25*i)))
        elif battleMode == 4: #print tools
            text_render = header_font.render("TOOLS (CLICK ON ENEMY TO USE ON ENEMY, CLICK ANYWHERE ELSE TO USE ON SELF)", True, (255,220,100) if selectedItem == 0 else (255,255,255))
            text_surf.blit(text_render, (10, 10))
            tools = player.GetTools()
            for i in range(len(tools)):
                text_render = font.render(f"{tools[i][0]:<20}Cost:{str(tools[i][1])+'EP':<5}{f'Charge:{tools[i][2]}/{tools[i][3]}' if tools[i][3] != -1 else '':<15}{'READY   ' if tools[i][4] else 'COOLDOWN'}  {tools[i][5]}", True, (255,255,255) if i != (selectedItem-1) else (255,220,100))
                text_surf.blit(text_render, (12, 40+(25*i)))
        else:
            for i in range(1,10):
                text_render = font.render("" if len(announcements) < i else announcements[-i], True, (255,255,255))
                text_surf.blit(text_render, (10, int(HEIGHT*0.3)-5-(25*i)))
        screen.blit(text_surf, (WIDTH*0.05, HEIGHT*0.70-60))

        bottom_surf.fill((0,0,0,255))
        HP, MaxHP, EP, MaxEP, DF, TempDF, ATK, TempATK, LVL, XP, XP_REQ = player.GetStats()
        bottom_render = header_font.render(f"HP:{f'{HP}/{MaxHP}':<10}EP:{f'{EP}/{MaxEP}':<10}DF:{f'{DF}' if TempDF == 0 else f'{DF} + {TempDF}':<10}ATK:{f'{ATK}' if TempATK == 0 else f'{ATK} + {TempATK}':<10}LVL:{LVL:<10}XP:{f'{XP}/{XP_REQ}':<10}", True, (255, 255, 255))
        bottom_surf.blit(bottom_render, (10, 10))
        screen.blit(bottom_surf, (0, HEIGHT-50))

        mousepos = pygame.mouse.get_pos()
        for enemy in enemies:
            if enemy[1].collidepoint(mousepos):
                info_surf.fill((0, 0, 0, 200))
                info_header_render = header_font.render(enemy[2].Name, True, (255, 220, 100))
                info_surf.blit(info_header_render, (10, 10))
                lines = enemy[2].GetInfoText().split('\n')
                for i in range(len(lines)):
                    info_render = font.render(lines[i], True, (255, 255, 255))
                    info_surf.blit(info_render, (10, 45+(i*30)))
                screen.blit(info_surf, mousepos)

        pygame.display.flip()
        clock.tick(FPS)

        if len(enemies) == 0:
            announcements.append(f"You win!!")
            pygame.time.delay(2000)
            isBattling = False

    pygame.quit()
    sys.exit()
