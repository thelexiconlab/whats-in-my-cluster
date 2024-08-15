# this file takes raw data from excel and corrects it using a 'corrections' file
# making it ready for forager analysis

import pandas as pd
import numpy as np


def corrections(raw_file, corrections_file):
    # read in the raw data
    raw = pd.read_csv(raw_file, names=['SID', 'response', 'rt'], header=None)

    # read in the corrections file
    corrections = pd.read_excel(corrections_file)

    # make a copy of the raw data to work with
    corrected = raw.copy()

    # iterate over the corrections file
    for i, row in corrected.iterrows():
        # for each entry, look up if there is a correction to be made
        # get the entry name
        word = row['response']
        # remove all special characters and spaces
        word = ''.join(e for e in word if e.isalnum())
        # remove all special characters and spaces from corrections file
        corrections['entry'] = corrections['entry'].apply(lambda x: ''.join(e for e in x if e.isalnum()))

        # see if there is a correction for this entry
        correction = corrections[corrections['entry'] == word]
        # if there is a correction, then see if the "final_evaluation" column contains EXCLUDE or REPLACE
        # if EXCLUDE, then remove the row from the corrected dataframe
        # if REPLACE, then replace the value in the "response" column with the value in the "final_word" column
        if correction.shape[0] > 0:
            if correction['final_evaluation'].values[0] == 'REPLACE':
                corrected.at[i, 'response'] = correction['final_word'].values[0]
        # remove all blank rows
        corrected = corrected.dropna()
        
    return corrected

raw_file = 'data/input_files/animals_words.csv'
corrections_file = 'data/input_files/animal_corrections.xlsx'

corrected = corrections(raw_file, corrections_file)
corrected.to_csv('data/input_files/animals_corrected.csv', index=False, encoding='utf-8-sig')


