#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 12:18:58 2024

@author: Yannick
"""

#%%Load packages
import pandas as pd
import os
from fuzzywuzzy import fuzz

#%% Set the directory
path = "/Users/Yannick/Documents/Thesis 2024"
os.chdir(path)

#%% load data
placenames = pd.read_excel("Data/placenames_sri.xlsx", sheet_name="alloetkoer_corle", header=None)
tokened_sentences = pd.read_csv("output/datasets/NER_tokenedsentences_alternative.csv", sep=';')

#create location set
alloetkoer_placenames = set(placenames.loc[placenames[1] == "alloetkoer corle", 0])

#load the document data
generale_missiven_large = pd.read_csv("Data/generale_missiven.csv")
generale_missiven = generale_missiven_large[["LabelIdentifier", "DocumentContent"]]

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
areas_list = ["alloetkoer corle", "hina corle", "happitigam corle"]

#Initiate list for promising sentences
promising_sentences = []

#Iterate over the areas so the placenames can be identified
for area in areas_list:
    
    #Print the area for tracking progress
    print(area)
    
    #filter out locations that give problems with matching
    problematic_locations = ["oeddetoetterepittige", "talloewatteheenpittie"]

    # Filter out problematic locations
    filtered_placenames = placenames.loc[~placenames[0].isin(problematic_locations)]
    
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
        if index % 100000 == 0:
            print(index)
      
#Create df from the list
promising_sentences = pd.DataFrame(promising_sentences)
    
#%%find the documents before and after the page where the promising sentence is found

# Remove trailing dot from the "LabelIdentifier" column
promising_sentences["LabelIdentifier"] = promising_sentences["LabelIdentifier"].str.rstrip(".")

# Function to generate labels before and after
def generate_labels(label):
    last_four_numbers = int(label.split("_")[-1])
    label_before = label[:-4] + str(last_four_numbers - 1).zfill(4)
    label_after = label[:-4] + str(last_four_numbers + 1).zfill(4)
    return label_before, label, label_after

# Duplicate the df to find additional labels
duplicated_df = pd.concat([promising_sentences]*3, ignore_index=True)

#initiate empty df to store the labels in
labels = pd.DataFrame()

# Apply the function to each row of the DataFrame
labels["LabelBefore"], labels["Label"], labels["LabelAfter"] = zip(*promising_sentences["LabelIdentifier"].apply(generate_labels))

# Concatenate the labels before, original labels, and labels after into a single column
all_labels = pd.concat([labels["LabelBefore"], labels["Label"], labels["LabelAfter"]], ignore_index=True)

#Put in the df
duplicated_df["labels"] = all_labels

#%%merge the df with the generale missiven
#remove the dot from the generale missiven label
generale_missiven["labels"] = generale_missiven["LabelIdentifier"].str.rstrip(".")

#Drop the unnecessary columns
generale_missiven = generale_missiven.drop('LabelIdentifier', axis=1)
duplicated_df = duplicated_df.drop('LabelIdentifier', axis=1)


#%% merge the df
promising_text = pd.merge(duplicated_df, generale_missiven, on="labels", how="inner")
promising_text = promising_text.sort_values(by='labels').reset_index(drop=True)

promising_text = promising_text[["labels", "DocumentContent", "location", "area", "match"]]

#%% wrtie csv for checking
promising_text.to_csv("output/datasets/promising_text.csv", index=False, sep=';')





