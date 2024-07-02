#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:19:06 2024

@author: Yannick
"""

#%%Load packages
import pandas as pd
import os
import nltk
from flair.data import Sentence

#%% Set the directory
path = "/Users/Yannick/Documents/Thesis 2024"
os.chdir(path)

#%%Load data
NER_results_Ceylon = pd.read_csv("output/datasets/NER_Ceylon.csv")

#%% Extract the names entities and create a list of placenames

# Function to split values at commas and return a single list of named entities
def split_and_concatenate(row):
    if isinstance(row, str):
        entities = row.split(", ")  # Split the string by comma and space
        return entities
    else:
        return []


# Apply the function to each row of the DataFrame
NER_results_Ceylon['listed_values'] = NER_results_Ceylon['NamedEntities'].apply(lambda x: split_and_concatenate(x))

#%% define functions
#define a function to search through the set
def find_locations(sentence, location_set):
    found_locations = []
    for token in sentence:
        if token.text in location_set:
            found_locations.append(token.text)
    found_locations = set(found_locations)
    found_locations = ', '.join(found_locations)
    return found_locations

#Define function for extracting locations
def extract_locations(NER_output):
    #Loop over the locations to find locations with at least 2 characters
    NER_output_filtered = [loc for loc in NER_output if len(loc) > 2]
    locations_from_function = set(NER_output_filtered)
    return locations_from_function


#%%

NER_tokenedsentences_Ceylon = []

for index, row in NER_results_Ceylon.iterrows():
    text = row['DocumentContent']  # Extract the content
    NER_output = row['listed_values']  # Extract locations
    locations_set = extract_locations(NER_output)
    sentences = nltk.sent_tokenize(text, language="Dutch")  # Tokenize into sentences with NLTK tokenizer for Dutch
    sentence_counter = 1  # Initiate the sentence number
    
    # Iterate over the sentences of the current document
    for sentence in sentences:
        # Tokenize the sentence
        tokenized_sentence = Sentence(sentence)
        
        # Check if the sentence has at least four tokens and less then 30 to make the checking easier
        if len(tokenized_sentence.tokens) > 4:
            locations = find_locations(tokenized_sentence, locations_set)
            sentence_list = []
            for token in tokenized_sentence:
                if token.text != ",":
                    sentence_list.append(token.text)
            NER_tokenedsentences_Ceylon.append({'LabelIdentifier': row['LabelIdentifier'], 'SentenceNumber': sentence_counter, 'sentence': sentence, 'sentence_list': sentence_list, 'locations': locations, })
            sentence_counter += 1  # Increase the sentence number by 1
    if index % 25000 == 0:
        print(index)
#%%
# Convert the list of dictionaries to a DataFrame
NER_tokenedsentences_Ceylon = pd.DataFrame(NER_tokenedsentences_Ceylon)

#%% Filter for rows where 'locations' list is not empty
survey_locations = NER_tokenedsentences_Ceylon[NER_tokenedsentences_Ceylon['locations'].apply(lambda x: len(x) > 0)]
survey_nolocations = NER_tokenedsentences_Ceylon[NER_tokenedsentences_Ceylon['locations'].apply(lambda x: len(x) == 0)]
        
#%% Sample both so that from each type there are 75
survey_sample = survey_locations.sample(50, random_state = 4)
sample_nolocations = survey_nolocations.sample(n=50, random_state=4)

# Append the sample to survey_mette
survey_sample = pd.concat([survey_sample, sample_nolocations])

#%% randomize the order
survey_sample = survey_sample.sample(frac=1, random_state=42)

#%% Save the dataframe
survey_sample.to_csv("output/Survey/survey_sample.csv", index=False, sep=';')

        
        
        
        
        