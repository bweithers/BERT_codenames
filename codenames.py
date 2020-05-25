import pandas as pd
import random as rd
from collections import OrderedDict
from math import floor, sqrt
from termcolor import colored, cprint
from english_words import english_words_lower_alpha_set

RECORDS_FILE = 'records.txt'
WORDS_FILE = 'wordlist.txt'
DISTANCES_FILE = 'similarities.txt'
RED_FILE = 'red.txt'
BLUE_FILE = 'blue.txt'
TITLE_FILE = 'title.txt'
BOMB_FILE = 'bomb.txt'
class Team:
   name = 'DEFAULT'
   players = []
   other = None
   num_remaining = -1
   bomb = False
   past_hints = []
   past_hint_nums = []
   yolo = 5

   def __init__(self, name, n_blue, yolo = 5, players = []):
       self.name = name
       self.yolo = yolo
       self.players = players
       if name == 'Blue':
           self.num_remaining = n_blue
           self.other = 'Red'
       elif name == 'Red':
           self.num_remaining = n_blue - 1
           self.other = 'Blue'

   def give_hint(self, board, turbo = False, comp_spy = False):
           hint, hint_num = "", -1
           print(f"It is {self.name}'s turn to play. They have {self.num_remaining} spaces remaining to get.")     
           print_board(board, turn = self.name) 
           if turbo:
               print('Turbo mode skips hints.')
               return "TURBO",100
           # Take in the hint word
           if comp_spy:
               return get_comp_hint(self,board, yolo = self.yolo)
           while hint == "":
               hint = input('Enter a single word hint: ')
               try: 
                   board.index(hint)
                   print('Please do not enter a word on the board as a hint.')
                   hint = ""
               except:
                   break
           while len(hint.split()) > 1:
               print("You're a cheating fucker, single word hint.")
               hint = input('Enter a single word hint: ')
           # Take in hint number
           while hint_num == -1:
               try:
                   hint_num = int(input('For how many? '))
               except ValueError:
                   print('No seriously, give a number.')
           self.past_hints.append(hint)
           self.past_hint_nums.append(hint_num)
           return hint, hint_num

   def print_history(self):
       print(f'History for {self.name}')
       for x,y in zip(self.past_hints, self.past_hint_nums):
           print(f'{x} for {y}', end = '\t')
       print()
       return 0
   
   def guess(self, board, hint,hint_num):        
        # Handle guesses
        guesses = 0
        while guesses < hint_num and self.num_remaining > 0:
            guess_word = input('What word do you think is related to the hint? ').lower()
            if guess_word == 'pass':
                return 0
            elif guess_word == 'hints':
                self.print_history()
                continue
            while True:
                try:
                    outcome = board[board.index(guess_word)].guess()
                    break
                except ValueError:
                    print('You have to guess a word that is in the board.')
                    guess_word = input('What word do you think is related to the hint? ').lower()
            while outcome == 'IDIOT':
                guess_word = input('What word do you think is related to the hint? ')
                if guess_word == 'hints':
                    self.print_history()
                    continue
                outcome = board.index(guess_word).guess()
            if outcome == self.name:
                guesses += 1
                self.num_remaining -= 1
                if guesses < hint_num:
                    print_board(board, self.name) 
                    print(f'You got one! Keep going, you have {hint_num - (guesses)} guesses left this turn and {self.num_remaining} words left to get to win.')
                    print(f'The hint was: {hint}')
                else:
                    print('You got one, but your turn is over since you are out of guesses.')
                
            elif outcome == 'BOMB':
                self.bomb = True
                return 'BOMB'
            elif outcome == 'NEUTRAL':
                print('\nYou hit a neutral word.\n')
                return 'NEUTRAL'
            elif outcome == self.other:
                print("\nHaha! You got the other team's square you fucking donkey.\n")
                return 'WRONG_COLOR'
        return 0
         
class Player:
    name = 'DEFAULT'
    team = 'DEFAULT'
    record = []
    def __init__(self, name = 'DEFAULT', team= 'DEFAULT'):
        self.name = name
        self.record = self.retrieve_record()
    def set_team(self,team):
        self.team = team
    def add_win(self):
        self.record[0] += 1
        return self.record[0]
    def add_loss(self):
        self.record[1] += 1
        return self.record[1]
    def retrieve_record(self, loc = RECORDS_FILE):
        record = [0,0]
        with open(loc, 'r') as f:
            for line in f:
                if self.name == line.split()[0]:
                    record = list(line.split[1], line.split[2])
                else:
                    continue
        return record
    def set_team(self, team):
        self.team = team
        return 0
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name 
    def __eq__(self,other):
        return self.name == other

class Space: 
   owner = 'DEFAULT'
   guessed = False
   word = '-1 debug'
   color = None
   distances = OrderedDict()
   def __init__(self, owner, word, distances):
       self.owner = owner
       self.word = word
       self.guessed = False 
       self.distances = distances 
   
   def guess(self):
       if self.guessed:
           print('You already guessed this space')
           return 'IDIOT'
       self.guessed = True
       if self.owner == 'BOMB':
           print('You guessed the bomb!')
           print(colored(open(BOMB_FILE, 'r').read(), 'magenta'))
       return self.owner

   def populate_distances(self):
       try:
           self.distances = sim_dict[self.word]
       except:
           print('Failed to get distances for {self.word}')
           return -1
       return 0

   def __eq__(self,other):
       return self.word == other

   def __str__(self):
       if self.guessed: 
           if self.owner == 'Red' or self.owner == 'Blue':
               return colored(self.word, self.owner.lower())
           elif self.owner == 'NEUTRAL':
               return colored(self.word, attrs = ['underline'])
           elif self.owner == 'BOMB':
               return colored(self.word, 'magenta')
       else:
           return self.word 
   def __repr__(self):
       return str(self)

def get_words(loc):
   word_list = []
   with open(loc) as f:
        for line in f:
            word_list.append(line.strip())
   return word_list

# This works to get ALL distances, just takes FOREVER
def get_distances(loc = DISTANCES_FILE):
   return (eval(open(loc,'r').read()))

# I have decided that blue always goes first
# No reason, just easier
def set_owners(size, n_blue):
   claimed = []
   blues = []
   reds = []
   bomb = -1 
   for i in range(n_blue):
       c = rd.randint(0, size-1)
       while c in claimed:
           c = rd.randint(0,size-1)
       blues.append(c)
       claimed.append(c)
   for i in range(n_blue - 1):
       c = rd.randint(0, size-1)
       while c in claimed:
           c = rd.randint(0,size-1)
       claimed.append(c)
       reds.append(c)
   while c in claimed:
       c = rd.randint(0,size-1)
   bomb = c
   return blues, reds, bomb
         
def set_words(size,word_list):
   words = []
   claimed = []
   for i in range(size):
       c = rd.randint(0, len(word_list) - 1)
       while c in claimed:
           c = rd.randint(0,len(word_list) -1)
       claimed.append(c)
       words.append(word_list[c])
   return words

# TODO
# Some function of YOLO and number such that
# Each successive barrier is less restricted
# But how quickly that barrier moves is defined by yolo
# TODO
# Return positive, negative thresholds such that 
# neutral/enemy/bomb words are (maybe) accounted for
# at a threshold that is not threshold or 1000 - threshold? 

def calc_threshold(hint_num, yolo):
    #print(f'calculating threshold with yolo: {yolo}')
    yolo_coeff_ = yolo / 10
    initial_barrier_ = ( 10 - yolo ) * 100 
    step_size_ = 100
    #return initial_barrier_
    return initial_barrier_ + hint_num *  yolo_coeff_ * step_size_ 


# TODO Fun Part :)
def get_comp_hint(team, board, yolo = 4, top = True, NOISE = 69, matches = []):
    # this intends to set YOLO to a value between one and ten, with ten being most aggressive
    # For example, if yolo is 4 then two words with similarity 600 would be considered a good hint
    # It would also consider all matching enemy words ( and the bomb ) above 400 as things to avoid
    #TODO
    threshold = ( 10 - yolo ) * 100
    if top:
        print(f'Thinking about a hint for {team.name}..')   
    # Remove words that we have decided are too close to the words on the board
    # This should only happen in recursive calls
    hint_pool = list(english_words_lower_alpha_set)
    for word in matches:
        try:
            hint_pool.remove(word)
        except ValueError:
            pass
    # Only care about our words
    # Pick really good words
    alleg = team.name
    my_spaces, enemy_spaces, neutral_spaces, bomb = [], [], [], None
    for space in board:
        if space.owner == alleg and not space.guessed:
            my_spaces.append(space)
        elif space.owner == team.other and not space.guessed:
            enemy_spaces.append(space)
        elif space.owner == 'BOMB':
            bomb = space
        elif space.owner == 'NEUTRAL' and not space.guessed:
            neutral_spaces.append(space)
        if space.word in hint_pool:
            hint_pool.remove(space.word)
    
        
        #for word in hint_pool:
            #tokens = nlp(word, space.word)
            #if tokens[0].lemma_ == tokens[1].lemma_:
            #    hint_pool.remove(word)
    max_key = 'DEFAULT'
    hint_words = []
    hint_scores = {x : [0,0] for x in hint_pool}
    hint_scores['DEFAULT'] = [-10000000,1]
    for space in my_spaces:
        for word in hint_pool:
            if word in team.past_hints or matches:
                continue
            try:
                # Noise is often nice to have because it means that the same words on the board
                # Do not always get the same hints, maybe this could be better fixed with good threshold
                score = space.distances[word] + rd.randint(0, NOISE)
                # How many words do we attribute to the score?
                # Higher yolo means 'bigger' hints, hints for more words
                #if score > calc_threshold(hint_scores[word][1], yolo):
                if score > threshold:
                    if score > calc_threshold(hint_scores[word][1], yolo):
                        hint_words.append(word)
                        hint_scores[word][0] += score
                        hint_scores[word][1] += 1

            except KeyError:
                #print(f'Failed to score hint from {space.word} to {word}')
                hint_scores[word][0] -= 100000000
                continue  
    
    enemy_spaces = []
    # TODO tune enemy avoidance
    for space in enemy_spaces:
        for word in hint_words:
            score = space.distances[word] + rd.randint(0, NOISE)
            if score > 1000 - threshold:
                hint_scores[word][0] -= hint_scores[word][1] * score
            else:
                hint_scores[word][0] -= ((10 - yolo) / 10) * score

    
    # TODO tune neutral avoidance
    for space in neutral_spaces:
        for word in hint_words:
            score = space.distances[word] + rd.randint(0, NOISE)
            if score > 1000 - threshold:
                hint_scores[word][0] -= (.25 * score)
    
    # TODO tune bomb avoidance
    for word in hint_words:
        score = bomb.distances[word] + rd.randint(0, NOISE) 
        if score > 1000 - threshold:
            hint_scores[word][0] -= (score)**2

    # TODO
    hint_prods = {k : v[0]  for k,v in hint_scores.items()}
    max_val = sorted(hint_prods.values(), reverse = True)[0]
    max_key = find_key(hint_prods, max_val)
    #print(f'Max hint val is: {max_val} it is from word {max_key}')
    #for k,v in hint_scores.items():
        #if v[1] != 0:
            #pass
            #print(f'Key: {k} Hint vals: {v}')
    hint,hint_num = max_key,hint_scores[max_key][1]
    
    # indefinite recursion... 'best practices' my ass
    # If you don't look its not there ;)
    # TODO
    if hint_num == 0:
        #print(f'No.. that hint doesnt work.. trying again')
        hint, hint_num = get_comp_hint(team,board,yolo = yolo+1, top = False)
    
    # Lazily removing hint word that are part of words on the board
    # Load-in time is already pretty long, so decided to do this
    # just in time
    matches = []
    illegal_flag = False
    for space in board:
        if (hint[:4] in space.word) or space.word[:4] in hint or hint[-4:] in space.word or space.word[-4:] in hint:
            matches.append(f'{hint} too close to {space.word}')
            illegal_flag = True 
    if illegal_flag:
        hint, hint_num = get_comp_hint(team, board, yolo+1, top = False, matches = matches)   
    if top:
        print(f'I think that "{hint}" for {hint_num} is a good hint.')
    
    team.past_hints.append(hint)
    team.past_hint_nums.append(hint_num) 
    return hint, hint_num

# Import only the similarity entries for words in words 
def get_distance_batch(words, loc = DISTANCES_FILE):
    sim_dict = {}
    with open(loc) as f:
        for line in f:
            brace_split = line.split('{')
            try:
                if brace_split[1][1:-3] == 'africa':
                    values = eval('{' + brace_split[2][:-2] )
                    sim_dict['africa'] = values
                    continue
            except IndexError:
                    pass
            key = brace_split[0][1:-3]
            if key in words:
                values = OrderedDict()
                values = eval("{" + brace_split[1][:-2])
                #values = eval(brace_split[1][:-3])
                sim_dict[key] = values
            else:
                continue
    return sim_dict

# Finds FIRST instance of value in dictionary d
# If no key is found with matching value, -1 is returned
def find_key(d, value):
    for k, v in d.items():
        if v == value:
            return k
    return -1

def make_board(size,n_blue):
   print(f'Setting up your game! This will just take a second..')
   board = []
   blues, reds, bomb = set_owners(size, n_blue)
   word_list = get_words(WORDS_FILE)
   sim_dict = get_distance_batch(word_list)
   words = set_words(size, word_list)
  
   #print(blues, reds, bomb)
   for i in range(size):
       if i in blues:
           board.append(Space('Blue', words[i], sim_dict[words[i]] ))
       elif i in reds:
           board.append(Space('Red', words[i], sim_dict[words[i]] ))
       elif i == bomb:
           board.append(Space('BOMB', words[i], sim_dict[words[i]] ))
       else:
           board.append(Space('NEUTRAL', words[i],sim_dict[words[i]] ))
   return board

def print_board(board,turn, spymaster = False):
   if turn == 'Red':
       for i in range(0):
           print()
       print(colored(open(RED_FILE).read(), 'red'))
   elif turn == 'Blue':
       for i in range(0):
           print()
       print(colored(open(BLUE_FILE).read(), 'blue'))
   cols = floor(sqrt(len(board)))
   for i in range(len(board)):
       if i % cols == 0:
           print()
       # janky rjust fix with bash color escape character sequence
       # :^)
       rjust_offset = 0
       if board[i].guessed:
           if board[i].owner == 'NEUTRAL':
               rjust_offset = 8
           else:
               rjust_offset = 9
       print(str(board[i]).rjust(30+rjust_offset), end = '')
   print()
   print() 
   return 0

def reveal_board(board, turn = ""):
    for space in board:
        space.guessed = True
    print_board(board, turn) 
    return 0

# TODO
def play_again(blue, red, players, comp_spy = True):
    if blue.num_remaining < 1 or red.bomb:
        print('BLUE wins!!')
    elif red.num_remaining < 1 or blue.bomb:
        print('RED wins!!!')
    again = input('Do you want to play again? y/n ')
    if again == 'y' or again == 'yes':
        same_teams = input('Do you want to use the same teams? y/n ')
        if same_teams == 'y':
            driver(comp_spy = comp_spy, players = players)
        else:
            driver(comp_spy = comp_spy, players = [])
    else:
        print('Thanks for playing!')
    return 0

def gameover(blue,red):
    retval = ''
    if blue.num_remaining < 1 or red.bomb:
        retval = 'Blue'
    elif red.num_remaining <1 or blue.bomb:
        retval = 'Red'
#    if retval == 'Blue':
#        for player in blue.players:
#            player.add_win()
#        for player in red.players:
#            player.add_loss()
#    elif retval == 'Red':
#        for player in blue.players:
#            player.add_loss()
#        for player in red.players:
#            player.add_win()

    return retval

def randomize_teams(players):
    blue_players = []
    red_players = []
    #print(len(players))
    team_size = len(players) / 2
    if len(players) % 2 == 1:
        team_size = len(players)//2 + 1
    for p in players:
        if len(blue_players) >= team_size:
            red_players.append(p)
        elif len(red_players) >= team_size:
            blue_players.append(p)
        else:
            blue_red = rd.randint(0,1)
 
            if blue_red == 1:
                blue_players.append(p)
            else:
                red_players.append(p)

    print(f'Teams are as follows: ')
    print(colored('Blue: ', 'blue'), end = ' ')
    for p in blue_players:
        print(str(p).rjust(10), end = ' ')
    print()
    print(colored('Red:  ', 'red'), end = ' ')
    for p in red_players:
        print(str(p).rjust(10), end = ' ')
    print()
    return blue_players, red_players

def make_teams(n_blue, players = []):
    # TODO track individual players so we can track their game score?
    blue_players = []
    red_players = []
    if not players:
        in_string = ''
        while in_string != 'done' and in_string != 'd':
            in_string = input('Enter the name of a player: ')
            if in_string == 'done' or in_string == 'd':
                break
            else:
                players.append(Player(in_string)) 
        in_string = ''
        while in_string != 'y' and in_string != 'n':
            in_string = str(input('Do you want the teams randomized for you? y/n '))
        if in_string == 'y':
            blue_players, red_players = randomize_teams(players)
        elif in_string == 'n':
            in_string = ''
            while in_string != 'done' and in_string != 'd':
                in_string = input('Enter the players for blue. The rest will be assigned to red. ')
                if in_string == 'done' or in_string == 'd' or len(blue_players) > (len(players) / 2):
                    blue_players.append(in_string)
            for p in players:
                if p.name not in blue_players:
                    red_players.append(p)  
    blue_yolo = -50
    while not(blue_yolo >= 1 and blue_yolo <= 10): 
        try:
            blue_yolo = int( input('Please input Blue YOLO value: (1 - 10 Higher is more aggressive hints.) ') )
        except ValueError:
            print('Enter an integer 1-10 you monkeys.')
    red_yolo = -50
    while not(red_yolo >= 1 and red_yolo <= 10): 
        try:
            red_yolo = int( input('Please input Red YOLO value:  (1 - 10 Higher is more aggressive hints.) ') )
        except ValueError:
            print('Enter an integer 1-10 you monkeys.')

    return Team('Blue', n_blue, players = blue_players, yolo = blue_yolo), Team('Red', n_blue, players = red_players, yolo = red_yolo), players

def print_title(loc= 'title.txt'):
    with open(loc, 'r') as f:
        print(f.read())

def driver(size=25, n_blue=9, turbo = False, comp_spy = False, players = []):
   print_title()
   if players:
       blue, red, players = make_teams(n_blue, players = players)
   else:
       blue, red, players = make_teams(n_blue)
   board = make_board(size, n_blue)
   turn = 'Blue'
   while not gameover(blue,red):
       if turn == 'Blue':
           hint,hint_num = blue.give_hint(board, turbo, comp_spy)
           outcome = blue.guess(board, hint,hint_num)
           if outcome == 'WRONG_COLOR':
               red.num_remaining -= 1
           elif outcome == 'BOMB':
               turn = 'BOMB'
               continue
           turn = 'Red'
           continue   
       elif turn == 'Red':
           hint,hint_num = red.give_hint(board, turbo, comp_spy)
           outcome = red.guess(board, hint,hint_num)
           if outcome == 'WRONG_COLOR':
               blue.num_remaining -= 1
           elif outcome == 'BOMB':
               turn = 'BOMB' 
               continue
           turn = 'Blue'
           continue    
   reveal_board(board, turn)
   play_again(blue, red, players)
   return 0
