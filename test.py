from codenames import *
from statistics import mean
test = input('What test do you want to run?').lower()

while test != 'quit' and test!='exit' and test!='q':
    
    # Takes arbitrary reference word and list of words to test distance from
    # list of words to reference word
    if test == 'distance':
        print(open('wordlist.txt','r').read())
        word, words = "", []
        while word != 'end':
            word = input('Enter a reference word.')
            words.append(word)
        sim_dict = get_distance_batch(words)
        spaces = []
        for word in words:
            spaces.append( Space('Red', word, sim_dict) )
        for space in spaces:
            print(space.distances)
            print(list( space.distances.values() ) )
        #for k,v in test_space.distances:
        #    print(f"{space_word} distance to {k}: {v}")
    elif test == 'comp spy':
        driver(25,9,comp_spy = True)
    elif test == 'turbo game':
        driver(18, 6, turbo = True)
    # Basic test of most features of the game
    elif test == 'full game':
        driver(15,3)
    test = input('Enter another test.')
