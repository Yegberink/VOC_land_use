#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 08:55:38 2024

@author: Yannick
"""

#%%Load packages
from fuzzywuzzy import fuzz
import pandas as pd
import os

#%% Set the directory
path = "/Users/Yannick/Documents/Thesis 2024"
os.chdir(path)

#%%Load data
placenames_map_ceylon = pd.read_excel("Data/placenames_sri.xlsx", sheet_name="alloetkoer_corle", header=None) #placenames in ceylon
placenames_documents_ceylon = pd.read_excel("Output/datasets/Dataset_ceylon_1723.xlsx", sheet_name="areas") #placenames in ceylon

#List of areas
areas_list = ["alloetkoer corle", "hina corle", "happitigam corle"]


#%%Define function
def find_matches(word, list_to_match, threshold=90):
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

    return matches  # Return the list of matches

#%%

matched_villages = []
# Create an empty list to store matched villages
matched_villages = []

for area in areas_list:
    # Filter the placenames map based on the current area
    filtered_placenames_map = placenames_map_ceylon[placenames_map_ceylon.iloc[:, 1] == area]
    
    # Extract the column with village names from the filtered map
    filtered_village_names = filtered_placenames_map.iloc[:, 0]
    
    # Iterate over the rows in placenames_documents_ceylon
    for _, row in placenames_documents_ceylon.iterrows():
        village = row["Village"]
        
        # Check if the village is not NaN
        if pd.notna(village):
            # Find matches
            matches = find_matches(village, filtered_village_names, threshold=80)
            
            # Append matches if any
            if matches:
                row_copy = row.copy()  # Make a copy of the row to avoid modifying the original DataFrame
                row_copy["Match"] = matches
                matched_villages.append(row_copy)

# convert matched_villages to a DataFrame
matched_villages_df = pd.DataFrame(matched_villages)


