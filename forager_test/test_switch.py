from forager.switch import *
from forager.cues import create_history_variables
import pandas as pd

fl_list = [
    "snake", "lion", "ox", "monkey", "fish", "shrimp", "octopus", "shark",
    "alligator", "crocodile", "frog", "gorilla", "horse", "cow", "pig", "chicken",
    "rabbit", "squirrel", "bear", "cheetah", "giraffe", "elephant", "dolphin", "lizard",
    "jellyfish", "zebra", "gazelle", "deer", "fox", "coyote", "wolf", "elephant",
    "whale", "porcupine", "peacock", "chicken", "turkey", "owl", "eagle", "eel",
    "platypus", "donkey", "mouse", "dog", "cat", "ferret", "guinea pig", "hamster"
]

animalnormspath =  'data/norms/animals_snafu_scheme_vocab.csv'
similaritypath =  'data/lexical_data/animals/semanticsimilaritymatrix.csv'
frequencypath =  'data/lexical_data/animals/frequencies.csv'
phonpath = 'data/lexical_data/animals/phonmatrix.csv'

animalnorms = pd.read_csv(animalnormspath, encoding="unicode-escape")
similarity_matrix = np.loadtxt(similaritypath,delimiter=',')
frequency_list = np.array(pd.read_csv(frequencypath,header=None,encoding="unicode-escape")[1])
phon_matrix = np.loadtxt(phonpath,delimiter=',')
labels = pd.read_csv(frequencypath,header=None)[0].values.tolist()

history_vars = create_history_variables(fl_list, labels, similarity_matrix, frequency_list, phon_matrix)

switch_delta(fl_list, history_vars[0], 0.75, 0.75) 