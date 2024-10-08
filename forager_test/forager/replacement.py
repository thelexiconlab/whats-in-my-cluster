
###to check a list of words from an csv file to check the needed replacements


import pandas as pd 
import gensim.downloader as api
from alive_progress import alive_bar


class replacement: 
    
    '''
        Description: 
            This class contains functions that create a data.csv file from a list of words
            from a file given as argument with information on which words are replaced for 
            getting the embeddings. 
            
        Functions: 
            (1) __init__ : creates data.csv 
            (2) word_checker : checks if word is in fasttext model 
            (3) collect_words : preprocesses the list of words. 
    
    '''
    
    
    
    def __init__(self, list_words, domain_name): 
        
        self.path = '../data/lexical_data/' + domain_name
        # self.model = api.load('fasttext-wiki-news-subwords-300')
        self.model_vocab = pd.read_csv('../data/models/fasttext_words.csv')['0'].values.tolist()
        
        # list words 
        self.original_words = [*set(list_words)]
        og_num = 0
        self.original_words_included = [] 
        for word in self.original_words: 
            if word in self.model_vocab: 
                self.original_words_included.append("included")
            else: 
                self.original_words_included.append("not included")
                og_num += 1

        

        # words after collect_words function
        self.collected_words = replacement.collect_words([x.replace("_","-") for x in self.original_words])
        self.collected_words_included = []
        collected_num = 0 
        for word in self.collected_words:
            if word in self.model_vocab: 
                self.collected_words_included.append("included")
            else: 
                self.collected_words_included.append("not included")
                collected_num += 1 
        
        
        replacement_num = 0 
        with alive_bar(len(self.collected_words)) as bar: 
            self.replacement = []
            for word in self.collected_words: 
                if word == replacement.word_checker(word):
                    self.replacement.append("N/A")
                else: 
                    self.replacement.append(replacement.word_checker(word))
                    replacement_num +=1
                bar()
        
        self.df = pd.DataFrame(list(zip(self.original_words, self.original_words_included, self.collected_words, self.collected_words_included, self.replacement)), columns= ['Original Words', 'Vocab', 'Modified Words', 'Vocab', 'Replacement'])
        self.df.to_csv(self.path + '/replacements.csv') 
        
        
    def word_checker(word): 
        '''
            Description: 
                Takes word (x) and if the word is not in fasttext's vectors. If there is no possible replacement
                that is in fasttext's vectors, we return "None" 
                 
            Args: 
                (1) word (str): word to check if it is in vectors. 
            Returns: 
                (1) replacement (str): the replacement word for the original word 
        ''' 
        
        df = pd.read_csv('../data/models/fasttext_words.csv')
        model_vocab = df['0'].values.tolist()
        
        if word in model_vocab:
            return word
        elif word.upper() in model_vocab: 
            return word.upper() 
        elif word.lower() in model_vocab: 
            return word.lower() 
        elif word.capitalize() in model_vocab: 
            return word.capitalize()
        elif word.replace("-", "") in model_vocab: 
            return word.replace("-", "")
        elif word.replace("-", "").capitalize() in model_vocab: 
            return word.replace("-", "").capitalize()
        elif word.replace("-", "").upper() in model_vocab: 
            return word.replace("-", "").upper()
        elif word.replace("-", "").lower() in model_vocab: 
            return word.replace("-", "").lower()
        
        split =  word.replace("-", " ").split()
        possibilities = []
        for words in split: 
            if words in model_vocab: 
                possibilities.append(words)
        
        if len(possibilities) == 0:
            return "unk"

        replacement = possibilities[-1]
        
        return replacement 
    
    def collect_words(list_of_words):
        '''
        Description: 
            Preprocesses the list of words. The words are turned into lowercase, add an underscore for spaces, 
            removes all unnecessary characters, remove consecutive duplicate words, and spell checks the words. 
        
        Args: 
            (1) List of words to standardize for forager usage. 
        
        Returns: 
            List of adjusted words 
        '''

        # turn words lowercase, add underscore for spaces, remove all unneccesary characters. 
        words = [x.lower() for x in list_of_words]
        words = [x.strip() for x in words]
        
        characters = [" ", "_""[", "]", "//", ".", '\\', ",", "'", '"', "|", "`", "/", "{", "}", ":", ";", "<", ">", "?", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "+", "=", "~"]
        for char in characters: 
            if char == " " or char == "_": 
                words = [x.replace(char, "-") for x in words]
            else: 
                words = [x.replace(char, "") for x in words]
            
        # removes consecutive duplicates 
                        
        return words 
    
    
# a = replacement('data/models/psyrev_data.csv', '0')
# b = replacement('data/fluency_lists/fovacs_occupations.xlsx', 'spellcheck')
# c = replacement('data/fluency_lists/fovacs_foods.xlsx', 'spellcheck')

