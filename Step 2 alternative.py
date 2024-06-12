#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 08:37:56 2024

@author: Yannick
"""

#%%Load packages
import pandas as pd
import os
from flair.data import Sentence

#%% Set the directory
path = "/Users/Yannick/Documents/Thesis 2024"
os.chdir(path)

#%% Load data
NER_results = pd.read_csv("output/datasets/NER_generale_missiven.csv")

#%%
# Function to split values at commas and return a single list of named entities
def split_and_concatenate(row):
    if isinstance(row, str):
        entities = row.split(", ")  # Split the string by comma and space
        return entities
    else:
        return []


# Apply the function to each row of the DataFrame
NER_results['listed_values'] = NER_results['NamedEntities'].apply(lambda x: split_and_concatenate(x))

#%%
example = NER_results.sample(300)
#%% define functions

#Define function for extracting locations
def extract_locations(NER_output):
    #Loop over the locations to find locations with at least 2 characters
    NER_output_filtered = [loc for loc in NER_output if len(loc) > 2]
    locations_from_function = set(NER_output_filtered)
    return locations_from_function

#%%
df_step2_1 = []

#Split the dataframe because of memory constraints
# Determine the midpoint index of the dataframe
midpoint_index = len(NER_results) // 2

# Split the dataframe into two halves
df1 = NER_results.iloc[:midpoint_index]
df2 = NER_results.iloc[midpoint_index:]

#Df 1
for index, row in df1.iterrows():
    text = row['DocumentContent']  # Extract the content
    NER_output = row['listed_values']  # Extract locations
    locations_set = extract_locations(NER_output)
    
    tokenized_text = Sentence(text)
    
    context_window = 30
    for i, token in enumerate(tokenized_text):
        if token.text in locations_set:
            start_index = max(0, i - context_window)
            end_index = min(len(tokenized_text), i + context_window + 1)
            context_tokens = tokenized_text[start_index:end_index]
            context_text = ', '.join(token.text for token in context_tokens if token.text.strip(" ") != ",")
            df_step2_1.append({'LabelIdentifier': row['LabelIdentifier'], 'sentence': context_text, 'location': token.text})
            
    if index % 50000 == 0:
        print(index)

# Convert the list of dictionaries to a DataFrame
df_step2_1 = pd.DataFrame(df_step2_1)


#%% df2

df_step2_2 = []

for index, row in df2.iterrows():
    text = row['DocumentContent']  # Extract the content
    NER_output = row['listed_values']  # Extract locations
    locations_set = extract_locations(NER_output)
    
    tokenized_text = Sentence(text)
    
    context_window = 30
    for i, token in enumerate(tokenized_text):
        if token.text in locations_set:
            start_index = max(0, i - context_window)
            end_index = min(len(tokenized_text), i + context_window + 1)
            context_tokens = tokenized_text[start_index:end_index]
            context_text = ', '.join(token.text for token in context_tokens if token != ",")
            df_step2_2.append({'LabelIdentifier': row['LabelIdentifier'], 'sentence': context_text, 'location': token.text})
            
    if index % 50000 == 0:
        print(index)

# Convert the list of dictionaries to a DataFrame
df_step2_2 = pd.DataFrame(df_step2_2)

#Concatenate together
df_step2 = pd.concat([df_step2_1, df_step2_2], ignore_index=True)


#%% Save the results
df_step2.to_csv("output/datasets/NER_tokenedsentences_alternative.csv", index=False, sep=';')






