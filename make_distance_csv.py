import numpy as np
import pandas as pd
import spacy
from codenames import Space
import matplotlib.pyplot as plt
import seaborn as sns
from statistics import mean
from tqdm import tqdm
from english_words import english_words_lower_alpha_set
start = 0
end = 2

nlp = spacy.load('en')
count = 0

loc = 'wordlist.txt'
out = 'similarities.txt'
board_words = []
check_ids = []
check_words = []
sim_dict = {}
for x in nlp.vocab:
    if x.is_alpha and x.text in english_words_lower_alpha_set and x.has_vector:
        check_ids.append(x.orth)
        check_words.append(x.text)

with open(loc) as f:
    for line in f:
        board_words.append(line.strip())


current_words = board_words
for word in tqdm(current_words):
    print(f'Starting similarity calcuation for {word}')
    similarities = {}
    for x in tqdm(check_words):
        tokens = nlp(word + ' ' + x)
        similarities[x] = int ( tokens[0].similarity(tokens[1]) * 1000 )
    print(f'Finishing similarities for {word}')
    sim_dict[word] = similarities

with open(out, mode = 'w') as f:
    f.write('{')
    for key in sim_dict:
        out_string = f"'{str(key)}': {str(sim_dict[key])},\n"
        f.write(out_string)
    f.write('}')



#print(first_word)
#first_word_dict = {}
#first_space = Space('red', first_word)
#for x in check_words:
#    first_word_dict[x] = first_space.get_distance(x)
#print(first_word_dict)

#with open(loc) as f:
#    for line in f:
#        word = line.strip()
#        dist_list = []
#        for x in 
#            board_words[word] =   
#
#
#board_words = pd.read_
