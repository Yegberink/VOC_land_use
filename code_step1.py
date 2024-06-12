#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 08:53:46 2024

@author: Yannick
"""
#%%Load packages
import pandas as pd
from flair.data import Sentence
from flair.nn import Classifier
import os

#%%set wd
os.chdir("/Users/Yannick/Documents/Thesis 2024")

#%%Load data
generale_missiven_large = pd.read_csv("Data/generale_missiven.csv")
generale_missiven = generale_missiven_large[["LabelIdentifier", "DocumentContent"]]

#%% Load NER model
tagger = Classifier.load("nl-ner-large")

#%% apply the model to the generale missiven
for i in range(len(generale_missiven)):
    k = i + 366370
    print(k) # to keep track of the progress
    content = generale_missiven.iloc[k, 1]  # Extract the question from the second column
    
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
    generale_missiven.at[k, "NamedEntities"] = locations_string #Save data

  #%% Save the results
results_NER = generale_missiven
results_NER.to_csv("output/datasets/NER_generale_missiven.csv", index=False)
