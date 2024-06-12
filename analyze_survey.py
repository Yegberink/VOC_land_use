#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 11:03:50 2024

@author: Yannick
"""
#Load packages
import pandas as pd
import os
import matplotlib.pyplot as plt

#%% Set the directory
path = "/Users/Yannick/Documents/Thesis 2024"
os.chdir(path)

#%%load data
results_henk = pd.read_csv("Data/Surveys Step 2/survey Step 2 Henk.csv", header=None).transpose()
results_mette = pd.read_csv("Data/Surveys Step 2/survey Step 2 Mette.csv", header=None).transpose()
results_myrthe = pd.read_csv("Data/Surveys Step 2/survey Step 2 Myrthe.csv", header=None).transpose()
results_yannick = pd.read_csv("Data/Surveys Step 2/survey Step 2 Yannick.csv", header=None).transpose()

survey_mette = pd.read_csv("output/survey_step1/survey_mette.csv", sep=";")
survey_henk = pd.read_csv("output/survey_step1/survey_henk.csv", sep=";")
survey_myrthe = pd.read_csv("output/survey_step1/survey_myrthe.csv", sep=";")
survey_yannick = pd.read_csv("output/survey_step1/survey_yannick.csv", sep=";")

#%% Function for cleaning

def clean_survey(survey_results, survey_questions, name):
    # Delete first row
    survey_results = survey_results.iloc[1:]
    
    # Initialize lists to store sentences and locations
    cleaned_sentences = []
    cleaned_locations = []
    
    # Get the sentences and answers column
    sentences_column = survey_results[0] #Sentences
    answers_column = survey_results[1] #Answers
    
    # Filter for unwanted question
    sentences_uncleaned = sentences_column[sentences_column != "Welke van de gevonden locaties is geen echte locatie?"]
    answers_q1 = answers_column[sentences_column != "Welke van de gevonden locaties is geen echte locatie?"]
    
    #Extract answers to q2
    answers_q2 = answers_column[sentences_column == "Welke van de gevonden locaties is geen echte locatie?"].reset_index(drop=True)
    
    # Iterate over each sentence
    for sentence in sentences_uncleaned:
        split_text = sentence.split("\n")
        
        # Extracting the sentence
        sentence_out = split_text[0].split("Sentence: ")[-1]
        
        # Extracting the locations
        locations = split_text[2]
        
        # Append to lists
        cleaned_sentences.append(sentence_out)
        if locations != 'Locaties: In deze zin zijn geen locaties gevonden':
            listed_locations = locations.split("Locations: ")[-1].strip().split(", ")
            cleaned_locations.append(listed_locations)
        else:
            cleaned_locations.append(None)
    
    # Create a DataFrame
    cleaned_answers = pd.DataFrame({'sentence': cleaned_sentences, 'locations': cleaned_locations, 'answers_q1': answers_q1})
    
    #Split df again
    cleaned_answers_noloc = cleaned_answers[cleaned_answers['locations'].isna()]
    cleaned_answers_loc = cleaned_answers[~cleaned_answers['locations'].isna()].reset_index(drop=True)
    
    #Add this to the questions 2
    cleaned_answers_loc['answers_q2'] = answers_q2
    cleaned_answers_noloc['answers_q2'] = None
    
    #Add a column specifying whether there is a location or not
    cleaned_answers_loc['has_location'] = "yes"
    cleaned_answers_noloc['has_location'] = "no"

    #put dfs together
    answers_df = pd.concat([cleaned_answers_loc, cleaned_answers_noloc], ignore_index=True)
    
    output_df = pd.merge(answers_df, survey_questions[['sentence', 'LabelIdentifier', 'SentenceNumber']], on='sentence', how='left')
    output_df = output_df[['LabelIdentifier', 'SentenceNumber', 'sentence', 'locations', 'answers_q1', 'answers_q2', 'has_location']]
    output_df['person'] = name

    return output_df

#%%
cleaned_henk = clean_survey(results_henk, survey_henk, "henk")
cleaned_mette = clean_survey(results_mette, survey_mette, "mette")
cleaned_myrthe = clean_survey(results_myrthe, survey_myrthe, "myrthe")
cleaned_yannick = clean_survey(results_yannick, survey_yannick, "yannick")

survey_answers = pd.concat([cleaned_henk, cleaned_mette, cleaned_myrthe, cleaned_yannick], ignore_index=True)

#%%

# Define colors for each unique value in the 'person' column
color_map = {'person1': 'darkolivegreen', 'person2': 'steelblue', 'person3': 'salmon', 'person4': 'goldenrod'}

plt.figure(figsize=(10, 8))
# Use 'person' column for colors and aggregate counts using 'answers_q1'
graph = survey_answers.groupby(['answers_q1', 'person']).size().unstack().plot(kind='bar', color=color_map.values())

plt.xlabel('answers_q1')
plt.ylabel('Count')
plt.title('Distribution of answers to Question 1')

# Calculate total count for percentage calculation
total_count = survey_answers['answers_q1'].count()

# Annotating each bar with its percentage (without digits after the dot)
for p in graph.patches:
    width = p.get_width()
    height = p.get_height()
    x, y = p.get_xy()
    percentage = height / total_count * 100
    plt.annotate(f'{height}',  # Format without digits after the dot
                 (x + width / 2, y + height),
                 ha='center',
                 va='center',
                 xytext=(0, 5),
                 textcoords='offset points',
                 weight='bold')

plt.legend(title='Person')  # Add legend with title 'Person'

plt.show()

#%% prepare data for Scott's Pi







