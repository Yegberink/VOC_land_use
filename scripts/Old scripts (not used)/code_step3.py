#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 10:59:36 2024

@author: Yannick
"""
#Load packages
from fuzzywuzzy import fuzz
import pandas as pd
import os 
import re  
import numpy as np

#%% Set the directory
path = "/Users/Yannick/Documents/Thesis 2024"
os.chdir(path)

#%% load data
#Sentences
tokened_sentences = pd.read_csv("output/datasets/NER_tokenedsentences_alternative.csv", sep=';')

#Commodities
commodity_df = pd.read_table("Data/commodities.txt", header=None)
commodity_list = commodity_df[0].tolist() #Expand to list

#Oppervlaktematen
oppervlaktematen_df = pd.read_table("Data/oppervlaktematen.txt", header=None)
oppervlaktematen_list = oppervlaktematen_df[0].tolist() #Expand to list

#%% create functions

# Initiate sliding window function
def sliding_window(elements, window_size):
    """
    Extracts sliding windows of a specified size from a list.
    
    Parameters:
    elements (list): List of elements.
    window_size (int): Size of the sliding window.
    
    Returns:
    list: List of sliding windows.
    """
    if len(elements) <= window_size:
        return elements
    return [elements[i:i+window_size] for i in range(len(elements)- window_size + 1)]

# Create a function for finding the commodities
def find_matches(sentence_list, list_to_match, threshold=80, threshold2=90):
    """
    Finds matches in a sentence by fuzzy matching with a list of items.
    
    Parameters:
    sentence (str): Input sentence to search for commodities which is formatted according to a list.
    commodity_list (list): List of items for matching.
    threshold (int, optional): Minimum threshold for fuzzy matching. Defaults to 80.
    threshold2 (int, optional): Higher threshold for more exact matching used in combination with the sliding window. Defaults to 90.
    
    Returns:
    list: List of tuples containing (token, item, similarity_score).
    """
    matches = []  # Create empty list
    
    # Iterate over the tokens in the list
    for token in sentence_list:
        token = token.strip("'")  # Remove single quotes from both the beginning and end of the token
        for item in list_to_match:  # Iterate over the list of commodities to find occurrences
            similarity_score = fuzz.ratio(token.lower(), item.lower())  # Apply fuzzy matching 
            if similarity_score >= threshold:
                matches.append((token, item, similarity_score))  # Append the commodity list
                
            # # If the commodity does not represent the exact word there might be a window in which it is correct
            # else:
            #     for element in sliding_window(token, len(commodity)):
            #         similarity_score = fuzz.ratio(element.lower(), commodity.lower()) 
            #         if similarity_score >= threshold2:
            #             matches.append((token, commodity, similarity_score))  # Append the commodity list
    
    return matches  # Return the list of matches

#Function to check for the occurence of a number in the text
def has_number(sentence): #Takes a string so not the sentence list
    return bool(re.search(r'\d', sentence)) #use regular expression to find a number

#%% find the commodities and check for the occurence of numbers

commodity_list_kaneel = ["Caneel", "Kaneel"]

#Create empty list
rows_containing_commodities = []

#Iterate over the tokened_sentences
for index, row in tokened_sentences.iterrows():
    sentence = row['sentence'] #Extract the sentence list
    
    # Process the sentence because it is saved as a string instead of a list
    sentence = sentence.strip("[")  # Remove leading [
    sentence = sentence.strip("]")  # Remove trailing ]
    sentence_list = sentence.split(', ')  # Split the sentence
    
    #Check for the occurence of a number
    number_occurence = has_number(sentence)
    
    #Continue id there is a number
    if number_occurence:
        commodities = find_matches(sentence_list, commodity_list_kaneel, threshold=90) #Apply function
        #If there is a commodity found append the list
        if commodities:
            row['commodities'] = commodities
            rows_containing_commodities.append(row)
            
    #Track the process
    if index % 100000 == 0:
        print(index)

#%% make it into a dataframe      
rows_containing_commodities = pd.DataFrame(rows_containing_commodities)

# Reset the index
rows_containing_commodities.reset_index(drop=True, inplace=True)
#%% find oppervlaktematen
#Create empty list
rows_containing_oppervlakte = []


# Iterate over the rows in rows_containing_commodities
for index, row in rows_containing_commodities.iterrows():
    sentence = row['sentence']  # Extract the sentence list

    # Process the sentence because it is saved as a string instead of a list
    sentence = sentence.strip("[")  # Remove leading [
    sentence = sentence.strip("]")  # Remove trailing ]
    sentence_list = sentence.split(', ')  # Split the sentence

    # Find matches for surface area measurements
    oppervlaktes = find_matches(sentence_list, oppervlaktematen_list, threshold=90)

    # If surface area measurements are found, update the row and append it to the list
    if oppervlaktes:
        row['oppervlaktematen'] = oppervlaktes
        row['non_listed_sentence'] = ' '.join(sentence_list)
        rows_containing_oppervlakte.append(row)

    # Track the process
    if index % 100 == 0:
        print(index)

#%% make it into a dataframe       
rows_containing_oppervlakte = pd.DataFrame(rows_containing_oppervlakte)

# Reset the index
rows_containing_oppervlakte.reset_index(drop=True, inplace=True)

#%%
for sentence in rows_containing_oppervlakte['non_listed_sentence'].unique():
    print(sentence)


#%% save the df
sentences_to_check = pd.DataFrame(rows_containing_oppervlakte['non_listed_sentence'].unique())
#%%
rows_containing_oppervlakte.to_csv("output/datasets/sentences_for_checking.csv")



#%% Check for embeddings

#Empty list
embeddings = []

#first check the embeddings to be sure that there is no 
for word in commodity_list:
    for comparison in commodity_list:
        for element in sliding_window(comparison, len(word)):
            if element == word:
                embeddings.append({"word": word, "embedded_in": comparison})

#%%
embeddings = pd.DataFrame(embeddings)

#%%
embeddings_unique = np.concatenate((embeddings['embedded_in'].unique(), embeddings["word"].unique()))

filtered_commodities = [word for word in commodity_list if word not in embeddings_unique]
