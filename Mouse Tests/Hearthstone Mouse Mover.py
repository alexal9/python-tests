import cv2
import pyautogui as p
import numpy as np
import time, json, re, sys, string

class HS:
    # Hearthstone window size
    HEIGHT = 800
    WIDTH = 1280

    MAC_HEIGHT_BORDER = 45/2.0    # border for exit, minimize, etc.
    CONFIRM_HEIGHT = 70.0/800 * HEIGHT

    HD_SCREEN = True

    def __init__(self):
        sys.path.append(sys.path[0] + '/Images/')   # add image library to path

        self.height = HS.HEIGHT
        self.width = HS.WIDTH
        
        time.sleep(1)
        p.click(219, 361)
        im = p.screenshot('gamestart.png')
        l,t,w,h = p.locate('exit.png', 'gamestart.png')
        self.left = l/(1.0+HS.HD_SCREEN)
        self.top = (t+h-w)/(1.0+HS.HD_SCREEN) + HS.MAC_HEIGHT_BORDER
        self.right = self.left + self.width
        self.bottom = self.top + self.height

        self.minion_height = 126.0/800 * self.height
        self.minion_width = 104.0/1280 * self.width

        self.hand_y = self.bottom - 50

        self.cards_loc = { 1: {1: 14.2},
                           2: {1: 13, 2: 15.4},
                           3: {1: 11.9, 2: 14.2, 3: 16.5},
                           4: {1: 11, 2: 12.6, 3: 15.8, 4: 17.4},
                           5: {1: 10.6, 2: 12.4, 3: 14.2, 4: 16, 5: 17.8},
                           6: {1: 10.1, 2: 11.6, 3: 13.1, 4: 14.6,
                               5: 16.1, 6: 17.6},
                           7: {1: 10, 2: 11.3, 3: 12.6, 4: 13.9, 5: 15.2,
                               6: 16.5, 7: 17.8},
                           8: {1: 9.3, 2: 10.5, 3: 11.7, 4: 12.9, 5: 14.1,
                               6: 15.3, 7: 16.5, 8: 17.7},
                           9: {1: 9.3, 2: 10.4, 3: 11.5, 4: 12.6, 5: 13.7,
                               6: 14.8, 7: 15.9, 8: 17, 9: 18.1},
                           10: {1: 9, 2: 10, 3: 11, 4: 12, 5: 13, 6: 14,
                                7: 15, 8: 16, 9: 17, 10:18} }

        #cards_file = open('cards.collectible.json','r',encoding='utf-8').read()
        #self.card_list = json.loads(cards_file)
        self.threshold_file = open('threshold.txt','r')
        s = self.threshold_file.read().strip()
        exec('self.threshold_dict = ' + s)
        

    def end_turn(self):
        p.click(self.left + 5, self.top + 5)    # ensure HS is active window
        p.click(self.endturn, self.center_line)

        
    def mulligan(self, num, cards = [], choose = False):
        """ 
        Mulligans the selected list of cards. Assumes that the card indices
        start from 1 and are between 3 or 4 (inclusive) depending on the
        number of cards, num, available to mulligan (the parameter num must
        either be 3 or 4.
        """
        cx, cy = p.center( (self.left, self.top, self.width, self.height) )
        
        self.center_line = cy - HS.MAC_HEIGHT_BORDER
        self.endturn = (23.5+1.6)/29.5 * self.width + self.left

        if num == 3:
            inc = 0.2 * self.width
            xstart = cx - inc

        if num == 4:
            xstart = round(8.2/29.5 * self.width)
            inc = 0.15 * self.width

        p.click(self.left + 5, self.top + 5)    # ensure HS is active window
        p.moveTo(xstart, cy)                    # move to start position

        for card_num in cards:
            p.click(xstart + (card_num-1)*inc, cy)        

        if not choose:
            p.click(cx, cy + self.height/4 + HS.CONFIRM_HEIGHT/2)
        
        self.cx = cx
        self.cy = cy

        self.hero_y = self.center_line + self.height/4 + HS.CONFIRM_HEIGHT/2
        self.enemy_y = self.center_line - self.height/4 - HS.CONFIRM_HEIGHT/2

        self.hero_power_xy = (self.cx + 130.0/1280*self.width, self.hero_y)
        

    def target(self, board_size, minion, enemy):
        """
        Here we assume that the board_size > 0, and the minion "index" starts
        at 1 and goes from left to right. If enemy flag is True, returns the
        minion position for the enemy minion. Max board size and minion index
        are both 7, and minion index cannot be greater than board size.
        """
        if not (-1 < board_size < 8) or not (-1 < minion < 8) \
           and minion > board_size:
            return

        if minion == 0:
             return (self.cx, self.enemy_y) if enemy else (self.cx, self.hero_y)
            
        minion_center = self.center_line + \
            (self.minion_height//2 if not enemy else -self.minion_height//2)
    
        if (board_size%2 == 1):
            return (self.cx + (minion-(board_size+1)//2)*self.minion_width,
                    minion_center)
        return (self.cx + (minion-board_size//2-0.5)*self.minion_width,
                 minion_center)


    def hero_power_target(self, target = [], use_hero = False):
        """
        This function assuming a targeting hero power, takes in a board_size,
        and a minion index (hero targeting is index 0). The function also
        takes in a use_hero flag, which is set to true if you use the hero
        to attack after using a hero power (Druid, Rogue). Also assumes
        correct input of board_size and minion index. Non-target version
        simply clicks on hero power.

        target = [ board_size , minion , enemy ]
        """
        p.click(self.left + 5, self.top + 5)    # ensure HS is active window
        x, y = h.hero_power_xy
        p.click(x, y)

        if target != []:
            if use_hero:
                self.hero_attack(target[0], target[1], target[2])
            else:
                loc_x, loc_y = self.target(target[0], target[1], target[2])
                p.moveTo(loc_x, loc_y, duration = 0.25)
                p.click()

        time.sleep(0.5)
 

    def hero_attack(self, board_size, minion):
        p.click(self.left + 5, self.top + 5)    # ensure HS is active window
        p.moveTo(self.cx, self.hero_y, duration = 0.25)
        if minion == 0:
            p.dragTo(self.cx, self.enemy_y, duration = 0.25)
        else:
            minion_x, minion_y = self.target(board_size, minion, True)
            p.dragTo(minion_x, minion_y, duration = 0.25)
        time.sleep(0.75)


    def minion_attack(self, board_size, minion, enemy_board_size, enemy_minion):
        """
        Similar concept to targeting with hero power. We find the location of
        our minion and the enemy minion (or hero) and we make the attack.
        """
        p.click(self.left + 5, self.top + 5)    # ensure HS is active window
        minion_x, minion_y = self.target(board_size, minion, False)
        p.moveTo(minion_x, minion_y)

        if enemy_minion == 0:
            p.dragTo(self.cx, self.enemy_y, duration = 0.25)
        else:
            enemy_x, enemy_y = self.target(enemy_board_size,
                                                    enemy_minion, True)
            p.dragTo(enemy_x, enemy_y, duration = 0.25)
        time.sleep(1)


    def attack_target(self, board_size, minion, enemy_board_size, enemy_minion,
                      on_attack = False):
        """
        Uses the functionality of minion_attack but concatenates successive
        minion attacks on the same target.
        """
        for size, m in zip(board_size, minion):
            self.minion_attack(size, m, enemy_board_size, enemy_minion)
            time.sleep(on_attack * 0.5)
            

    def play_card(self, hand_size, card, card_type, loc = None, target = []):
        """
        Plays a specific card from the hand with location designated by first
        the hand_size and then the number of the card (index starts at 1).
        card_type specifies whether or not the card to be played is a spell
        or minion, with a location specified in a target list.

        target = [ board_size , minion , enemy ]

        The information in target list is sent to target function to determine
        location of the specified target.

        loc = [ board_size , position ]

        loc is only used when a monster is to be played. The monster will
        either be played on the ends or in between 2 other minions specified
        by position.

        For example: if we have 3 minions on the board

                     [1]    |1|    [2]    |2|    [3]    |3|    [4]

            designated by | |, we have 3+1 positions available to place the
            minion (designated by [ ])
        """
        p.click(self.left + 5, self.top + 5)    # ensure HS is active window
        card_x = self.cards_loc[hand_size][card]/29.5 * self.width + self.left

        if card_type == 'spell':
            p.moveTo(card_x, self.hand_y)
            if target != []:
                x, y = self.target(target[0], target[1], target[2])
                p.dragTo(x, y, duration = 0.25)
            else:
                p.dragTo(self.cx, self.cy, duration = 0.25)
            
                
        elif card_type == 'minion':
            p.moveTo(card_x, self.hand_y)

            board_size, position = loc
            if position == board_size + 1:
                loc_x = self.target(board_size, board_size, False)[0] + \
                        self.minion_width/2
            else:
                loc_x = self.target(board_size, position, False)[0] - \
                        self.minion_width/2
            p.dragTo(loc_x, self.cy, duration = 0.25)
            if target != []:
                x, y = self.target(target[0], target[1], target[2])
                p.moveTo(x, y, duration = 0.25)
                p.click()
        time.sleep(0.75)

##############

    # Integration with OpenCV

    def find_minion(self, minion_name, threshold=0.93, modify=False):
        """
        Finds the location of a minion(s) through threshold detection. Some
        fine-tuning may be necessary if the function is unable to find the
        location of a minion (given that the minion exists on the board) given
        the current threshold value.

        NOTE: attack or health buffs can interfere with image detection.
        """
        p.click(self.left + 5, self.top + 5)    # ensure HS is active window
        p.screenshot('game.png')

        # Python 2.7
        table = string.maketrans("' .","---")
        minion_img = minion_name.translate(table).lower() + '.png'

        img_rgb = cv2.imread('game.png')
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(sys.path[-1] + minion_img,0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCORR_NORMED)

        if minion_img not in self.threshold_dict or modify:
            self.threshold_dict[minion_img] = threshold
            self.threshold_file.close()
            f = open('threshold.txt','w')
            f.write(str(self.threshold_dict))
            
        loc = np.where( res >= self.threshold_dict[minion_img])

        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
        cv2.imwrite('testpic.png',img_rgb)
        
        return loc
    

    def minion_loc(self, board_size, pixel):
        """
        Given a board size, x pixel coordinate, and an enemy flag, find the
        corresponding minion location.
        """
        pixel = pixel//(1+HS.HD_SCREEN)
        offset = (pixel-self.cx)//self.minion_width

        if board_size%2 == 0:
            return offset + board_size//2 + 1
        return offset + (board_size+1)//2 + 1
    

    def split_loc(self, loc):
        start = middle = end = 0
        for i in range(len(loc[0])):
            if loc[0][i] < \
               (self.center_line-self.minion_height)*(1+HS.HD_SCREEN):
                start = middle = i
            elif loc[0][i] < self.center_line*(1+HS.HD_SCREEN):
                middle = i
            elif loc[0][i] > \
                (self.center_line+self.minion_height)*(1+HS.HD_SCREEN):
                end = i
                break
        if end == 0:            # case for matches only on my board
            end = len(loc[0])
        print(start, middle, end)
        return (set(loc[1][start:middle]), set(loc[1][middle:end]))


    """
    def split_loc(loc):
        start = middle = end = 0
        for i in range(len(loc[0])):
            if loc[0][i] < 613:
                start = i
            elif loc[0][i] < 865:
                middle = i
            elif loc[0][i] > 1117:
                end = i
                break
        print(start, middle, end)
        return (set(loc[1][start:middle]), set(loc[1][middle:end]))
    """


    def process_loc(self, board_size, loc_set):
        temp = set()
        for pixel_loc in loc_set:
            temp_loc = self.minion_loc(board_size, pixel_loc)
            if 1 <= temp_loc <= board_size:
                temp.add(temp_loc)
        return list(temp)
                    

if __name__ == '__main__':
    h = HS()


