#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 11:26:55 2024

@author: Yannick
"""

#%% Load packages
import pandas as pd
import os
from flair.data import Sentence
from flair.nn import Classifier
from fuzzywuzzy import fuzz

#%% Set the directory
path = "/Users/Yannick/Documents/Thesis 2024"
os.chdir(path)

#%% Load data
files_df = pd.read_csv("Data/files.csv") #Text files
banda_labels = pd.read_table("Data/index_banda.txt", header=None) #Labels for banda documents

#%%
placenames_banda = pd.read_excel("Data/placenames_banda.xlsx", sheet_name="Sheet1", header=None) #placenames in banda

#%%
tokened_sentences = pd.read_csv("output/datasets/NER_tokenedsentences_banda.csv", sep=';')

#%%filter for the labels of banda
#Create set of complete labels
banda_labels_set = set("HaNA_1.04.02_" + banda_labels[0].astype(str))

#Create short number in the files used for filtering
files_df['file_number_short'] = files_df['LabelIdentifier'].apply(lambda x: '_'.join(x.split('_')[:-1]))

#Filter for the documents that concern banda
banda_documents = files_df[files_df["file_number_short"].isin(banda_labels_set)].reset_index(drop=True)

#Make smaller one with just the label and the content
banda_documents_clean = banda_documents[["LabelIdentifier", "DocumentContent"]]


#%% find the locations in the documents

#Load the NER model
tagger = Classifier.load("nl-ner-large")

#%% apply the model to the generale missiven
for i in range(len(banda_documents_clean)):
    
    k = i + 67475 #Add a number to make it possible to pause and continue
    print(k) # to keep track of the progress
    
    # Extract the question from the second column
    content = banda_documents_clean.iloc[k, 1]
    
    # make sentence (tokenisation) --> other tokenisers can be used this one just gives back the words
    sentence = Sentence(content)
    
    # predict NER tags
    tagger.predict(sentence)
    
    #extract the named entitiese 
    entities = sentence.get_spans('ner')
    
    # Initiate empty list
    location_words = []

    #Filter for locations  
    for span in entities:
        if span.tag == "LOC":
            location_words.append(span.text) #Append the list
            
    # Save the list of location words as a string in the dataframe
    locations_string = ', '.join(location_words)
    banda_documents_clean.at[k, "NamedEntities"] = locations_string #Save data

#%% Save the results
results_NER_banda = banda_documents_clean
results_NER_banda.to_csv("output/datasets/NER_banda.csv", index=False)

#%% define functions
# Function to split values at commas and return a single list of named entities
def split_and_concatenate(row):
    if isinstance(row, str):
        entities = row.split(", ")  # Split the string by comma and space
        return entities
    else:
        return []

#Define function for extracting locations
def extract_locations(NER_output):
    #Loop over the locations to find locations with at least 2 characters
    NER_output_filtered = [loc for loc in NER_output if len(loc) > 2]
    locations_from_function = set(NER_output_filtered)
    return locations_from_function

#%% split the NER results into lists
results_NER_banda['listed_values'] = results_NER_banda['NamedEntities'].apply(lambda x: split_and_concatenate(x))

#%%
tokened_sentences = []

#Extract the locations and save the 30 tokens around it

for index, row in results_NER_banda.iterrows():
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
            tokened_sentences.append({'LabelIdentifier': row['LabelIdentifier'], 'sentence': context_text, 'location': token.text})
            
    if index % 30000 == 0:
        print(index)

# Convert the list of dictionaries to a DataFrame
tokened_sentences = pd.DataFrame(tokened_sentences)

#%% Save the results
tokened_sentences.to_csv("output/datasets/NER_tokenedsentences_banda.csv", index=False, sep=';')

#%% Define functions

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

def find_matches(word, list_to_match, threshold=90, threshold2=90):
    """
    Finds matches to a word by fuzzy matching with a list of items.
    
    Parameters:
    word (str): Input word to match.
    list_to_match (list): List of items for matching.
    threshold (int, optional): Minimum threshold for fuzzy matching. Defaults to 80.
    threshold2 (int, optional): Higher threshold for more exact matching used in combination with the sliding window. Defaults to 90.
    
    Returns:
    list: List of tuples containing (word, item, similarity_score).
    """
    matches = []  # Create empty list
    
    # Iterate over the tokens in the list
    for item in list_to_match:  # Iterate over the list 
        similarity_score = fuzz.ratio(word.lower(), item.lower())  # Apply fuzzy matching to the item in the list and the word that has to be matched
        if similarity_score >= threshold:
            matches.append((word, item, similarity_score))  # Append the list
        
            # If the commodity does not represent the exact word there might be a window in which it is correct
        else:
            for element in sliding_window(word, len(item)): #Loop over the elements of the sliding window
                similarity_score = fuzz.ratio(element.lower(), word.lower()) 
                if similarity_score >= threshold2:
                    matches.append((word, item, similarity_score))  # Append the list
    
    return matches  # Return the list of matches

#%%find locations

#List of areas
areas_list = ["gunungapij", "neijra", "banda", "poelo aij", "poelo rhone", "rossingain", "poelo pissan"]

#Initiate list for promising sentences
promising_sentences = []

#Iterate over the areas so the placenames can be identified
for area in areas_list:
    
    #Print the area for tracking progress
    print(area)
    
    #filter out locations that give problems with matching
    problematic_locations = []

    # Filter out problematic locations
    filtered_placenames = placenames_banda.loc[~placenames_banda[0].isin(problematic_locations)]
    
    # Filter the filtered placenames to only have the current area
    placename_set = set(filtered_placenames.loc[filtered_placenames[1] == area, 0])
        
    #Iterate over the tokened_sentences df
    for index, row in tokened_sentences.iterrows():
        
        #Extract the location
        location = row["location"]
    
        #Apply the find_matches function to match the location on the map with a location mentioned in the texts
        found_match = find_matches(location, placename_set, threshold=95, threshold2=98)
            
        #If a match is found add the match and the area to the row and append dataframe
        if found_match:
            row["match"] = found_match #Add match
            row["area"] = area #Add area
            promising_sentences.append(row) #append df
            
        #Print index to track progress
        if index % 30000 == 0:
            print(index)
      
#Create df from the list
promising_sentences = pd.DataFrame(promising_sentences)


#%%merge the df with the generale missiven
#remove the dot from the generale missiven label
banda_documents["labels"] = banda_documents["LabelIdentifier"].str.rstrip(".")

# Remove trailing dot from the "LabelIdentifier" column
promising_sentences["labels"] = promising_sentences["LabelIdentifier"].str.rstrip(".")

#Drop the unnecessary columns
banda_documents = banda_documents.drop('LabelIdentifier', axis=1)
#duplicated_df = duplicated_df.drop('LabelIdentifier', axis=1)


#%% merge the df
promising_text_banda = pd.merge(promising_sentences, banda_documents, on="labels", how="inner")
promising_text_banda = promising_text_banda.sort_values(by='labels').reset_index(drop=True)

promising_text_banda = promising_text_banda[["labels", "DocumentContent", "location", "area", "match"]]

#%% wrtie csv for checking
promising_text_banda.to_csv("output/datasets/promising_text_banda.csv", index=False, sep=';')

#%% Find the documents that were deemed interesting after checking

#Load the set of numbers
interesting_document_numbers_banda = set(pd.read_table("Data/interesting_document_numbers_banda.txt", header=None)[0])

#Filter for these numbers
interesting_documents_banda = files_df[files_df["LabelIdentifier"].isin(interesting_document_numbers_banda)].reset_index(drop=True)

#%%Save the dataset for checking
interesting_documents_banda.to_csv("output/datasets/interesting_documents_banda.csv", index=False, sep=';')


