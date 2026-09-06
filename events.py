import pygame, sys
from random import randint, choices
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
                Name = enemy[1]
                stats = []
                for i in range(4,9):
                    if '~' in enemy[i]:
                        lo, hi = enemy[i].split('~')
                        stats.append(randint(int(lo), int(hi)))
                    else:
                        stats.append(int(enemy[i]))

                return models.Entity(Name, stats[0], stats[1], stats[2], stats[3], stats[4])
                

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

                
