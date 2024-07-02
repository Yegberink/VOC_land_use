#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 10:57:25 2024

@author: Yannick
"""

#%%Load packages
import os
import re
import pandas as pd

#%% Set the directory
path = "/Users/Yannick/Documents/Thesis 2024"
os.chdir(path)

#%%Create function
# Function to process each file
def process_file(file_path):
    """
    loads and processes VOC documents as being downloaded from the Globalize framework. 
    The formula takes in a file path to a document, removes the disclaimer, 
    and splits it according to the different pages.
    
    
    Parameters:
    file_path (str): path to the file to be processed
    
    Returns:
    pd.Dataframe: Dataframe with the content of one page per row and the a label to go along with that.
    """
    #Add a try except loop for if a file is in a different format
    try:
        #open the text file
        with open(file_path, 'r') as file:
            text = file.read()
        
        #Create the regex patterns for the disclaimer and the page headers
        disclaimer_pattern = r'\*{10,}.*?\*{10,}.*?(?=-{3,})'
        split_pattern = r'---\n(NL-HaNA_1\.04\.02_\d+[A-Za-z]*_\d+\.xml)\n---'
        
        #Find the disclaimer pattern and replace it with nothing
        text = re.sub(disclaimer_pattern, '', text)
        
        #Find the different pages in the document
        matches = re.findall(split_pattern, text)
        
        #Track the length of the documents and print an error message if there are none
        document_count = len(matches)
        if document_count == 0:
            print("No documents found in file:", file_path)
            return None
        
        #Initiate labels and document content
        label_identifiers = []
        document_content = []
        
        #Loop over the documents found in the matches
        for i in range(document_count):
            
            #Find start of the page
            start_pos = text.find(matches[i]) + 3
            
            #End of the page
            end_pos = text.find(matches[i + 1]) - 1 if i < document_count - 1 else len(text)
            
            #Extract tghe labels
            label_identifiers.append(text[text.find(matches[i]) + 3:text.find(matches[i]) + 28])
            
            #Extract the content
            document_content.append(text[start_pos:end_pos])
        
        #Create pandas dataframe
        df = pd.DataFrame({
            'LabelIdentifier': label_identifiers,
            'DocumentContent': document_content
        })

        return df
    
    #Print error message if there is something wrong with a file
    except Exception as e:
        print("An error occurred while processing file:", file_path)
        print(e)
        return None



#%%Process the files

# Load the file paths
file_paths = [os.path.join("Data", "VOC_data", file) for file in os.listdir("Data/VOC_data")]

# Loop over files to process them
files = [process_file(file_path) for file_path in file_paths]

# Remove None elements
files = [file for file in files if file is not None]

# Combine into a single dataframe
files_df = pd.concat(files, ignore_index=True)

#%%Clean up the labels 
files_df["LabelIdentifier"] = files_df["LabelIdentifier"].str.rstrip(".xm")

#%% Save the dataframe to a CSV file
files_df.to_csv("Data/files.csv", index=False)
