from random import random, randint

TOOL = "professional-looking value"
ITEM = "even more proffessional-looking value"
DAMAGE = "imagine typoeing the word 'professional' lol"
ELEC_DAMAGE = "Well imagining typoing the word 'typoing' double lol"

class Item():
    def __init__(self, Name, effects, useText = None, desc = None):
        '''effects are a list, where each effect in the list is in the format (string of attribute to change, True if multiplier or False if adder, intensity, cap stat if any)'''
        self.Name = Name
        self.type = ITEM
        self.effects = effects
        self.useText = ("used " + Name) if useText == None else useText
        self.desc = "" if desc == None else desc

    def UseItem(self, entity):
        '''Returns string of use text'''
        output = f"{entity.Name} {self.useText}.\n"
        for effect in self.effects:
            prev = getattr(entity, effect[0])
            if effect[1]:
                new = prev*effect[2] if len(effect) == 3 else min(prev*effect[2], getattr(entity, effect[3]))
                output += f"{entity.Name}'s {effect[0]} was multiplied by {effect[2]}.\n"
            else:
                new = prev+effect[2] if len(effect) == 3 else min(prev+effect[2], getattr(entity, effect[3]))
                output += f"{entity.Name}'s {effect[0]} was increased by {effect[2]}.\n"
            setattr(entity, effect[0], new)
        return output

class Tool():
    def __init__(self, Name, cost = 0, charge_max = -1, effects = [], useText = None, desc = None):
        '''effects are a list, where each effect in the list is in the format (string of attribute to change, True if multiplier or False if adder, intensity, cap stat if any)'''
        self.Name = Name
        self.type = TOOL
        self.cost = cost
        self.effects = effects
        self.useText = ("used " + Name) if useText == None else useText
        self.desc = "" if desc == None else desc
        self.charge = 0
        self.charge_max = charge_max

        self.isUsed = False

    def UseTool(self, user, target):
        '''Returns string of use text'''
        output = f"{user.Name} {self.useText} on {target.Name if user != target else 'themself'}.\n"
        for effect in self.effects:
            if effect[0] == DAMAGE:
                recv_damage = target.RecvDamage(effect[1])
                if recv_damage == False:
                    output += f"The {target.Name} dodged the attack!"
                else:
                    output += f"The {target.Name} took {recv_damage} damage."
            elif effect[0] == ELEC_DAMAGE:
                output += f"The {target.Name} took {target.RecvElecDamage(effect[1])} damage."
            else:
                prev = getattr(target, effect[0])
                if effect[1]:
                    new = prev*effect[2] if len(effect) == 3 else min(prev*effect[2], getattr(target, effect[3]))
                    output += f"{target.Name}'s {effect[0]} was multiplied by {effect[2]}.\n"
                else:
                    new = prev+effect[2] if len(effect) == 3 else min(prev+effect[2], getattr(target, effect[3]))
                    output += f"{target.Name}'s {effect[0]} was increased by {effect[2]}.\n"
                setattr(target, effect[0], new)
        return output

class Entity():
    def __init__(self, Name = "Entity", hp = 20, hp_max = None, ep = 10, ep_max = None, df = 2, atk = 5, lk = 5, cc = None, cf = None, dc = None, df_pw = None):
        ###MAIN STATS###
        self.Name = Name
        self.hp = hp #HEALTH
        self.hp_max = hp if hp_max == None else hp_max #MAX HP
        self.ep = ep #ENERGY
        self.ep_max = ep if ep_max == None else ep_max #MAX EP
        self.df = df #DEFENCE
        self.atk = atk #ATTACK FORCE
        self.lk = lk #LUCK
        self.cc = 0.03*lk if cc == None else cc #CRIT CHANCE
        self.dc = 0.02*lk if dc == None else dc #DODGE CHANCE
        self.cf = 2.5*atk if cf == None else cf #CRIT FORCE

        self.df_pw = df*2 if df_pw == None else df_pw #DEFENCE POWER: how much extra defence the player gets if they defended

        ###ITEMS###
        self.inv = {}

        ###TOOLS###
        self.tools = {}

        ###BATTLE STATS###
        self.effects = []
        self.atk_tmp = 0
        self.df_tmp = 0

    def GetStats(self):
        '''Returns HP, MaxHP, EP, MaxEP, DF, TempDF, ATK and TempATK'''
        return self.hp, self.hp_max, self.ep, self.ep_max, self.df, self.df_tmp, self.atk, self.atk_tmp

    def GameTick(self):
        '''Progresses the battle one turn forward. Lose one stack of effects and recharge all tools.'''
        self.ap_tmp, self.df_tmp = 0, 0
        for tool in self.tools.keys():
            self.tools[tool] = True

    def DealDamage(self):
        '''Returns if a crit occurred, followed by raw damage dealt'''
        if random() <= self.cc:
            return True, self.cf
        return False, self.atk

    def Defend(self):
        '''Gains df_pw in defence, returns extra df gained'''
        self.df_tmp += self.df_pw
        return self.df_pw

    def RecvDamage(self, damage=0):
        '''Change entity's hp by damage, affected by defence and dodge chance
        Returns False if dodged, else true damage dealt'''
        if random() < self.dc:
            return False
        true_damage = max(damage-self.df-self.df_tmp, 0)
        self.hp -= true_damage
        return true_damage

    def RecvElecDamage(self, damage=0):
        '''Change entity's hp by damage, affected by defence, but not dodge chance
        Returns true damage dealt'''
        true_damage = max(damage-self.df-self.df_tmp, 0)
        self.hp -= true_damage
        return true_damage

    def GainItem(self, item, count = 1):
        '''Adds an item to player's inventory'''
        for inv_item in self.inv.keys():
            if item.Name == inv_item.Name:
                self.inv[inv_item] += count
                return
        self.inv[item] = count

    def GetInventory(self):
        '''Returns list of items and amounts'''
        output = []
        for item, count in self.inv.items():
            output.append([item.Name, count])
        return output

    def RemoveItem(self, itemName):
        '''Removes 1 item from inventory, returns Item'''
        for item in self.inv.keys():
            if item.Name == itemName:
                self.inv[item] -= 1
                if self.inv[item] == 0:
                    self.inv.pop(item)
                return item

    def GainTool(self, tool):
        "Returns False if tool is already in inventory"
        for tools_tool in self.tools.keys():
            if tool.Name == tools_tool.Name:
                return False
        self.tools[tool] = True

    def GetTools(self):
        '''Returns list of tools, cost, charge, max charge, availability and description'''
        output = []
        for tool, isAvailable in self.tools.items():
            output.append([tool.Name, tool.cost, tool.charge, tool.charge_max, isAvailable, tool.desc])
        return output

    def UseTool(self, toolName):
        '''Makes a tool no longer available and consumes its cost, returns False if tool cannot be used or cost cannot be paid'''
        for tool in self.tools.keys():
            if tool.Name == toolName:
                if self.tools[tool] == True and self.ep >= tool.cost:
                    self.tools[tool] = False
                    self.ep -= tool.cost
                    return tool
                else:
                    return False

    def IsDead(self):
        '''Returns if entity is dead'''
        return self.hp <= 0

class Enemy(Entity):
    def __init__(self, Name = "Enemy", hp = 20, hp_max = None, ep = 10, ep_max = None, df = 2, atk = 5, lk = 5, cc = None, cf = None, dc = None, df_pw = None,desc = "", xp = 5, loot = []):
        super().__init__(Name, hp, hp_max, ep, ep_max, df, atk, lk, cc, cf, dc, df_pw)
        self.desc = desc
        self.xp = xp
        self.loot = loot
        
    def GetInfoText(self):
        '''Returns info window text about the enemy'''
        return f"HP:{self.hp}/{self.hp_max}\nEP:{self.ep}/{self.ep_max}\nATK:{self.atk}, DEF:{self.df}\nLCK:{self.lk}"

    def dropLoot(self):
        '''Returns dropped XP and loot'''
        return self.xp, self.loot if self.loot else None

class Player(Entity):
    def __init__(self, Name = "Player", hp = 20, hp_max = None, ep = 10, ep_max = None, df = 2, atk = 5, lk = 5, cc = None, cf = None, dc = None, df_pw = None):
        super().__init__(Name, hp, hp_max, ep, ep_max, df, atk, lk, cc, cf, dc, df_pw)
        self.lvl = 1
        self.xp = 0

    def GetStats(self):
        '''Returns HP, MaxHP, EP, MaxEP, DF, TempDF, ATK, TempATK, lvl, xp and required xp'''
        return self.hp, self.hp_max, self.ep, self.ep_max, self.df, self.df_tmp, self.atk, self.atk_tmp, self.lvl, self.xp, 10*self.lvl

    def gainXP(self, xp):
        '''Returns True if player leveled up'''
        self.xp += xp
        if self.xp > 10*self.lvl:
            self.xp -= 10*self.lvl
            self.lvl += 1
            self.hp_max += 5
            self.hp += 5
            self.atk += 1
            self.df += 1
            return True
    
