import numpy as np
from scipy import stats
import statistics
from scipy.optimize import curve_fit
import difflib
import pandas as pd
from forager.sung_SVD import calculate_svd_clusters, gtom_clusters
from forager.cues import create_history_variables


'''
Methods for calculating switches in Semantic Foraging methods.
    Current Methods:
        (1) Similarity Drop (simdrop): Switch Heuristic used in Hills TT, Jones MN, Todd (2012), where a switch is 
            predicted within a series of items A,B,C,D after B if S(A,B) > S(B,C) and S(B,C) < S(C,D)

        (2) Troyer Norms: Switch Method based on Categorization Norms developed in Troyer, AK, Moscovitch, M, & Winocur, G (1997).
            Switches are predicted when moving from one category from the "Troyer Norms" to another.

        (3) Multimodal Simdrop: An extension of the Similarity Drop Method to include phonological similarity in the heuristic

        (4) Delta Similarity: A method for predicting switches proposed by Nancy Lundin in her dissertation to bypass limitations
            of simdrop model, and allow for consecutive switches, and accounts for small dips in similarity that simdrop may
            deem a switch, which may actually be due to "noise" 

    Output Format: 
        Each switch method should preserve the same length/general format for returing switch values, 
        which can then be used in the foraging models, passed as a parameter

        length: each switch list should be the same length as the fluency_list
        coding: 
            0 - no switch
            1 - switch predicted by method
            2 - boundary case
    
'''


def switch_simdrop(fluency_list, semantic_similarity):
    '''
        Similarity Drop Switch Method from Hills TT, Jones MN, Todd (2012).
        
        Args:
            fluency_list (list, size = L): fluency list to predict switches on
            semantic_similarity (list, size = L): a list of semantic similarities between items in the fluency list, obtained via create_history_variables

        Returns:
            a list, size L, of switches, where 0 = no switch, 1 = switch, 2 = boundary case
    '''
    simdrop = []
    for k in range(len(fluency_list)):
        if (k > 0 and k < (len(fluency_list)-1)): 
            # simdrop
            if (semantic_similarity[k+1] > semantic_similarity[k]) and (semantic_similarity[k-1] > semantic_similarity[k]):
                simdrop.append(1)
            
            else:
                simdrop.append(0)

        else:
            simdrop.append(2)

    return simdrop

def switch_norms_categorical(fluency_list,norms):
    '''
    Hills et al. 2015 categorical switches where a switch is predicted if the category of the current word is different than the shared category of the previous two words

    Args:
        fluency_list (list, size = L): fluency list to predict switches on
        norms (dataframe, size = L x 2): dataframe of norms data matching animals to a categorical classification
    Returns:
        categorical (list, size = L): a list of switches, where 0 = no switch, 1 = switch, 2 = boundary case
    '''
    df = pd.DataFrame({'item': fluency_list, 'designation': [-1] * len(fluency_list)})

    items_in_norms = norms['Item'].values.tolist()

    def find_most_recent_one_index(lst, index):
        for i in range(index - 1, -1, -1):
            if lst[i] == 1 or lst[i] == 2:
                return i
        return index # if no 1s or 2s are found, return the current index

    for i, row in df.iterrows():
        if i == 0:
            df.at[i, 'designation'] = 2
        elif i == 1:
            # find category of previous word
            prev_word = df.loc[i - 1, 'item']
            closest_match = difflib.get_close_matches(prev_word, items_in_norms, n=1)
            prev_word = closest_match[0] if len(closest_match) > 0 else prev_word
            
            prev_word_cats = norms[norms['Item'] == prev_word]['Category'].tolist() if prev_word in items_in_norms else 'notinnorms'
            #print("cat for {} is {}".format(prev_word, prev_word_cats))
            
            # find category of current word
            current_word = row['item']
            closest_match = difflib.get_close_matches(current_word, items_in_norms, n=1)
            current_word = closest_match[0] if len(closest_match) > 0 else current_word
            current_word_cats = norms[norms['Item'] == current_word]['Category'].tolist() if current_word in items_in_norms else 'notinnorms'
            #print("cat for {} is {}".format(current_word, current_word_cats))
            
            # check if they share a category
            if any(cat in current_word_cats for cat in prev_word_cats):
                df.at[i, 'designation'] = 0
                #print("shared category")
            else:
                df.at[i, 'designation'] = 1
                #print("different category")
        else:
            
            prev_one = find_most_recent_one_index(df['designation'], i)
            cluster = df.loc[prev_one:i, :]
            prev_words = norms[norms['Item'].isin(cluster['item'])]
            prev_cats = prev_words.groupby('Item', group_keys=False)['Category'].apply(list).to_dict()
            #print("cat for {} is {}".format(prev_words, prev_cats))
            
            all_shared_cats = set.intersection(*[set(cats) for cats in prev_cats.values()]) if len(prev_cats) > 0 else set()
            # find category of current word
            current_word = row['item']
            closest_match = difflib.get_close_matches(current_word, items_in_norms, n=1)
            current_word = closest_match[0] if len(closest_match) > 0 else current_word
            current_word_cats = norms[norms['Item'] == current_word]['Category'].tolist() if current_word in items_in_norms else 'notinnorms'
            #print("cat for {} is {}".format(current_word, current_word_cats))
            
            if any(cat in current_word_cats for cat in all_shared_cats):
                df.at[i, 'designation'] = 0
                #print("shared category")
            else:
                df.at[i, 'designation'] = 1
                #print("different category")
    
    # return the designations
    categorical_designations = df['designation'].values.tolist()
    return categorical_designations

def switch_norms(fluency_list,norms):
    '''
        Switch Method Based on Troyer Norms from Troyer, A. K., Moscovitch, M., & Winocur, G. (1997).

        Args:
            fluency_list (list, size = L): fluency list to predict switches on
            norms (dataframe, size = L x 2): dataframe of norms data matching animals to a categorical classification

        Returns:
            troyer (list, size = L): a list of switches, where 0 = no switch, 1 = switch, 2 = boundary case
    '''
    norm_designation = []

    for k in range(len(fluency_list)):
        if k > 0:
            item1 = fluency_list[k]
            item2 = fluency_list[k-1]
            items_in_norms = norms['Item'].values.tolist()
            # find closest match to item1 and item2 in norms
            # often, this will be an exact match, but if not, we want to find the closest match
            # so that we can assign the category of the closest match to item1 and item2
            # e.g., grapes -> grape
            # if difflib returns an empty list, then there is no close match, and we just use the original item
            
            item1 = difflib.get_close_matches(item1, items_in_norms, n=1)[0] if len(difflib.get_close_matches(item1, items_in_norms, n = 1)) > 0 else item1
            item2 = difflib.get_close_matches(item2, items_in_norms, n=1)[0] if len(difflib.get_close_matches(item2, items_in_norms, n = 1)) > 0 else item2

            category1 = norms[norms['Item'] == item1]['Category'].values.tolist()
            category2 = norms[norms['Item'] == item2]['Category'].values.tolist()

            if len(list(set(category1) & set(category2)))== 0:
                norm_designation.append(1)

            else:
                norm_designation.append(0)

        else:
            norm_designation.append(2)
    
    return norm_designation

def switch_multimodal(fluency_list,semantic_similarity,phonological_similarity,alpha):
    '''
        Multimodal Similarity Drop based on semantic and phonological cues, extending Hills TT, Jones MN, Todd (2012).
        Args:
            fluency_list (list, size = L): fluency list to predict switches on
            semantic_similarity (list, size = L): a list of semantic similarities between items in the fluency list, obtained via create_history_variables
            phonological_similarity (list, size = L): a list of phonological similarities between items in the fluency list obtained via create_history_variables
            alpha (float): alpha parameter that dictates the weight of semantic vs. phonological cue, between 0 and 1
        Returns:
            multimodalsimdrop (list, size = L): a list of switches, where 0 = no switch, 1 = switch, 2 = boundary case
        
        Raises:
            Exception: if alpha is not between 0 and 1
    '''    
    #Check if alpha is between 0 and 1
    
    if alpha > 1 or alpha < 0:
        raise Exception("Alpha parameter must be within range [0,1]")
    simphon = alpha * np.array(semantic_similarity) + (1 - alpha) * np.array(phonological_similarity)
    multimodalsimdrop = []

    for k in range(len(fluency_list)):
        if (k > 0 and k < (len(fluency_list) - 1)): 
            if (simphon[k + 1] > simphon[k]) and (simphon[k - 1] > simphon[k]):
                multimodalsimdrop.append(1)
            else:
                multimodalsimdrop.append(0)

        else:
            multimodalsimdrop.append(2)

    return multimodalsimdrop

def switch_multimodaldelta(fluency_list, semantic_similarity, phonological_similarity, rise_thresh, fall_thresh, alpha):
    '''
        Delta Similarity Switch Method proposed by Nancy Lundin & Peter Todd. 
        
        Args:
            fluency_list (list, size = L): fluency list to predict switches on
            semantic_similarity (list, size = L): a list of semantic similarities between items in the fluency list, obtained via create_history_variables
            rise_thresh (float): after a switch occurs, the threshold that the increase in z-scored similarity must exceed to be a cluster  
            fall_thresh (float): while in a cluster, the threshold that the decrease in z-scored similarity must exceed to be a switch

        Returns:
            a list, size L, of switches, where 0 = no switch, 1 = switch, 2 = boundary case
    '''
    if rise_thresh > 1 or rise_thresh < 0:
        raise Exception("Rise Threshold parameter must be within range [0,1]")

    if fall_thresh > 1 or fall_thresh < 0:
        raise Exception("Fall Threshold parameter must be within range [0,1]")
    
    if alpha > 1 or alpha < 0:
        raise Exception("Alpha parameter must be within range [0,1]")
    
    simphon = alpha * np.array(semantic_similarity) + (1 - alpha) * np.array(phonological_similarity)

    switchVector = [2] # first item designated with 2

    # obtain consecutive semantic similarities b/w responses
    # z-score similarities within participant
    similaritiesZ = stats.zscore(simphon[1:])
    medianSim = statistics.median(similaritiesZ)
    meanSim = 0
    similaritiesZ = np.concatenate(([np.nan], similaritiesZ))

    # define subject level threshold = median (zscored similarities)
    # firstSwitchSimThreshold = meanSim
    firstSwitchSimThreshold = medianSim
    # for second item, if similarity < median, then switch, else cluster
    if similaritiesZ[1] < firstSwitchSimThreshold:
        switchVector.append(1)
    else:
        switchVector.append(0)

    currentState = switchVector[1]
    previousState = currentState

    # for all other items:
    for n in range(1,len(fluency_list)-1):
    #   consider n-1, n, n+1 items
        
        simPrecedingToCurrentWord = similaritiesZ[n]
        
        simCurrentToNextWord = similaritiesZ[n+1]
        if previousState == 0: #if previous state was a cluster
            if fall_thresh < (simPrecedingToCurrentWord - simCurrentToNextWord): # similarity diff fell more than threshold
                currentState = 1 # switch
            else:
                currentState = 0 # cluster
        else: # previous state was a switch
            if rise_thresh < (simCurrentToNextWord - simPrecedingToCurrentWord): # similarity diff is greater than our rise threshold
                currentState = 0 # cluster
            else:
                currentState = 1 # switch

        switchVector.append(currentState)
        previousState = currentState

    return switchVector


def switch_delta(fluency_list, semantic_similarity, rise_thresh, fall_thresh):
    '''
        Delta Similarity Switch Method proposed by Nancy Lundin & Peter Todd. 
        
        Args:
            fluency_list (list, size = L): fluency list to predict switches on
            semantic_similarity (list, size = L): a list of semantic similarities between items in the fluency list, obtained via create_history_variables
            rise_thresh (float): after a switch occurs, the threshold that the increase in z-scored similarity must exceed to be a cluster  
            fall_thresh (float): while in a cluster, the threshold that the decrease in z-scored similarity must exceed to be a switch

        Returns:
            a list, size L, of switches, where 0 = no switch, 1 = switch, 2 = boundary case
    '''
    if rise_thresh > 1 or rise_thresh < 0:
        raise Exception("Rise Threshold parameter must be within range [0,1]")

    if fall_thresh > 1 or fall_thresh < 0:
        raise Exception("Fall Threshold parameter must be within range [0,1]")

    switchVector = [2] # first item designated with 2

    # obtain consecutive semantic similarities b/w responses
    # z-score similarities within participant
    #print("semantic_similarity: ", semantic_similarity)
    similaritiesZ = stats.zscore(semantic_similarity[1:])
    #print("similaritiesZ: ", similaritiesZ)
    medianSim = statistics.median(similaritiesZ)
    #print("medianSim: ", medianSim)
    meanSim = 0
    similaritiesZ = np.concatenate(([np.nan], similaritiesZ))

    # define subject level threshold = median (zscored similarities)
    # firstSwitchSimThreshold = meanSim
    firstSwitchSimThreshold = medianSim
    # for second item, if similarity < median, then switch, else cluster
    if similaritiesZ[1] < firstSwitchSimThreshold:
        switchVector.append(1)
        #print(f"{fluency_list[1]} is a switch")
    else:
        switchVector.append(0)
        #print(f"{fluency_list[1]} is a cluster")

    currentState = switchVector[1]
    previousState = currentState

    # for all other items:
    for n in range(1,len(fluency_list)-1):
    #   consider n-1, n, n+1 items
        
        simPrecedingToCurrentWord = similaritiesZ[n]
        #print(f"similarity of {fluency_list[n]} to {fluency_list[n+1]}: {simPrecedingToCurrentWord}")
        
        simCurrentToNextWord = similaritiesZ[n+1]
        #print(f"similarity of {fluency_list[n+1]} to {fluency_list[n+2]}: {simCurrentToNextWord}")
        if previousState == 0: #if previous state was a cluster
            if fall_thresh < (simPrecedingToCurrentWord - simCurrentToNextWord): # similarity diff fell more than threshold
                currentState = 1 # switch
            else:
                currentState = 0 # cluster
            #print(f"current state: {currentState}")
        else: # previous state was a switch
            if rise_thresh < (simCurrentToNextWord - simPrecedingToCurrentWord): # similarity diff is greater than our rise threshold
                currentState = 0 # cluster
            else:
                currentState = 1 # switch
            #print(f"current state: {currentState}")

        switchVector.append(currentState)
        previousState = currentState

    return switchVector

def switch_svd_gtom(fluency_list, svd_clusters, gtom_threshold):
    """
        SVD-GTOM Switch Method proposed by Sung et al. (2013)
        
        Args:
            fluency_list (list, size = L): fluency list to predict switches on
            svd_clusters (list, size = L): a list of svd clusters for each word in the fluency list, obtained via calculate_svd_clusters
            gtom_threshold (float): threshold for GTOM clustering

        Returns:
            a list, size L, of switches, where 0 = no switch, 1 = switch, 2 = boundary case
    """
    
    cluster_vector = [] 
    # loop through list of words
    for i in range(len(fluency_list)):
        if i >0:
            wordpair = (fluency_list[i], fluency_list[i - 1])
            # check if wordpair is clustered
            if gtom_clusters(word_clusters=svd_clusters, target_words=wordpair, threshold=gtom_threshold):
                cluster_vector += [0]
            else:
                cluster_vector += [1]
        else:
            cluster_vector += [2]
    return cluster_vector

def exponential_curve(x, c, m):
    return c * (1 - np.exp(-m * x))

def fit_exponential_curve(reaction_times):
    x = np.arange(1, len(reaction_times)+1)
    # Adjusted initial parameter guesses
    c_guess = max(reaction_times)  # Set initial guess for c to the maximum data value
    m_guess = 0.01

    # Parameter bounds
    parameter_bounds = ([0, 0], [2 * max(reaction_times), 1])  # Constrain c to [0, 2 * max(y)] and m to [0, 1]

    # Fit the curve
    popt, _ = curve_fit(exponential_curve, x, reaction_times, p0=[c_guess, m_guess], bounds=parameter_bounds, maxfev=10000)

    # Fit the exponential curve to the data
    
    fitted_curve = exponential_curve(x, *popt)
    #print("Fitted curve: ", fitted_curve)

    # Calculate slope differences and classifications
    classifications = np.zeros(len(x))
    for i in range(len(x)):
        if i == 0:
            classifications[i] = 2
        else:
            fitted_slope_difference = fitted_curve[i] - fitted_curve[i - 1]
            raw_slope_difference = reaction_times[i] - reaction_times[i - 1]
            if fitted_slope_difference > raw_slope_difference:
                # fitted RT is higher than raw RT
                classifications[i] = 0
            else:
                # fitted RT is lower than raw RT
                classifications[i] = 1
         
    return classifications.tolist()

# fit_exponential_curve([0, 3.941, 6.041, 8.041, 10.041, 12.441, 14.441, 16.441, 18.441, 21.641, 
#                23.541, 27.441, 32.741, 35.641, 38.541, 40.741, 42.841, 44.941, 47.241, 
#                49.641, 52.141, 55.041, 57.841, 60.841, 64.541, 69.141, 73.841, 76.641, 
#                80.041, 82.841, 85.141, 87.741, 93.041, 109.741, 113.141, 116.341, 
#                120.141, 125.741, 131.741, 133.941, 141.141, 143.441, 150.041, 155.141, 
#                158.541, 160.741, 163.741, 166.541])

# animalnormspath =  '../data/norms/animals_snafu_scheme_vocab.csv'
# switch_norms_categorical(["snake", "lion", "ox", "monkey", "fish", "shrimp", "octopus", 
#                    "shark", "alligator", "crocodile", "frog", "gorilla", "horse", 
#                    "cow", "pig", "chicken", "rabbit", "squirrel", "bear", "cheetah", 
#                    "giraffe", "elephant", "dolphin", "lizard", "jellyfish", "zebra", 
#                    "gazelle", "deer", "fox", "coyote", "wolf", "elephant", "whale", 
#                    "porcupine", "peacock", "chicken", "turkey", "owl", "eagle", "eel", 
#                    "platypus", "donkey", "mouse", "dog", "cat", "ferret", "guinea pig", 
#                    "hamster"], pd.read_csv(animalnormspath, encoding="unicode-escape"))

