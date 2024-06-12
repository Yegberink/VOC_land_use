# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 14:04:08 2024

@author: Yannick
"""

#%%Load packages
import pandas as pd
import os
import math
import nltk
from flair.data import Sentence

#%% Set the directory
path = "/Users/Yannick/Documents/Thesis 2024"
os.chdir(path)

#%% Load data
NER_results = pd.read_csv("output/datasets/NER_generale_missiven.csv")

#%% Extract the names entities and create single list of placenames

# Function to split values at commas and return a single list of named entities
def split_and_concatenate(row):
    if isinstance(row, str):
        entities = row.split(", ")  # Split the string by comma and space
        return entities
    else:
        return []


# Apply the function to each row of the DataFrame
NER_results['listed_values'] = NER_results['NamedEntities'].apply(lambda x: split_and_concatenate(x))

# Concatenate all lists into a single vector
named_entities_vector = NER_results['listed_values'].explode().tolist()

# Remove nan values
cleaned_data = [x for x in named_entities_vector if not (isinstance(x, float) and math.isnan(x))]

#Sort the named entities
named_entities_sorted = sorted(cleaned_data) 

#%%Create list of unique values
# find unique values
unique_locations = NER_results['listed_values'].explode().unique().tolist() #Find unique locations

#%%
#Remove nan values
unique_locations = [x for x in unique_locations if not (isinstance(x, float) and math.isnan(x))] 

#Sort the named entities
unique_locations = sorted(unique_locations) 
#%%
unique_locations_filtered = [loc for loc in unique_locations if len(loc) > 2]

#%%Divide into sentences

results = [] #initiate empty list

# Iterate through each text and divide into sentences
for index, row in NER_results.iterrows():
    text = row['DocumentContent'] #Extract the content
    sentences = nltk.sent_tokenize(text, language="Dutch") #tokenize into sentences with nltk tokenizer  for Dutch
    sentence_counter = 1 #Initiate the sentence number
    
    #iterate over the sentences of the current document
    for sentence in sentences:
        #Append the results list
        results.append({'LabelIdentifier': row['LabelIdentifier'], 'SentenceNumber': sentence_counter, 'sentence': sentence})
        sentence_counter += 1 #increase the sentence number by 1
    if index % 100000 == 0: #print the index to keep track of progress
        print(index)

# Create DataFrame from results
result_df = pd.DataFrame(results)

#%% tokenize the sentences into words
result_df['TokenedSentence'] = None #initiate empty column

#Loop over the dataframe
for i in range(len(result_df)):
    sentence = result_df.iloc[i, 2] #Extract the sentence
    tokenized = Sentence(sentence) #Tokenize the sentence with the same tokenizer as in step 1 to get the same tokens (hopefuly)
    if len(tokenized.tokens) > 4:
        result_df.at[i, 'TokenedSentence'] = tokenized
    #track the progress
    if i % 1000000 == 0:
        print(i)

#%%
# Filter the DataFrame to remove rows where TokenedSentence is None
result_df_filtered = result_df.dropna(subset=['TokenedSentence'])

# Reset the index after filtering
result_df_filtered.reset_index(drop=True, inplace=True)

#%%Extract the sentence list to use for saving in csv
results_to_csv = []

for index, row in result_df_filtered.iterrows():
    tokenies = row['TokenedSentence']
    sentence_list = []
    for token in tokenies:
        if token.text != ",":
            sentence_list.append(token.text)
    row['sentence_list'] = sentence_list
    results_to_csv.append(row)
    if index % 500000 == 0:
        print(index)

# Convert the list of dictionaries to a DataFrame
results_to_csv = pd.DataFrame(results_to_csv)



#%% Sample the dataframes to be used in the next steps for checking
sample = result_df_filtered.sample(n=200, random_state=40).reset_index(drop=True)

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
df_step2_1 = []
df_step2_2 = []

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
    sentences = nltk.sent_tokenize(text, language="Dutch")  # Tokenize into sentences with NLTK tokenizer for Dutch
    sentence_counter = 1  # Initiate the sentence number
    
    # Iterate over the sentences of the current document
    for sentence in sentences:
        # Tokenize the sentence
        tokenized_sentence = Sentence(sentence)
        
        # Check if the sentence has at least four tokens
        if len(tokenized_sentence.tokens) > 4:
            locations = find_locations(tokenized_sentence, locations_set)
            sentence_list = []
            for token in tokenized_sentence:
                if token.text != ",":
                    sentence_list.append(token.text)
            df_step2_1.append({'LabelIdentifier': row['LabelIdentifier'], 'SentenceNumber': sentence_counter, 'sentence': sentence, 'sentence_list': sentence_list, 'locations': locations, })
            sentence_counter += 1  # Increase the sentence number by 1
    if index % 50000 == 0:
        print(index)

# Convert the list of dictionaries to a DataFrame
df_step2_1 = pd.DataFrame(df_step2_1)

#df2
for index, row in df2.iterrows():
    text = row['DocumentContent']  # Extract the content
    NER_output = row['listed_values']  # Extract locations
    locations_set = extract_locations(NER_output)
    sentences = nltk.sent_tokenize(text, language="Dutch")  # Tokenize into sentences with NLTK tokenizer for Dutch
    sentence_counter = 1  # Initiate the sentence number
    
    # Iterate over the sentences of the current document
    for sentence in sentences:
        # Tokenize the sentence
        tokenized_sentence = Sentence(sentence)
        
        # Check if the sentence has at least four tokens
        if len(tokenized_sentence.tokens) > 4:
            locations = find_locations(tokenized_sentence, locations_set)
            sentence_list = []
            for token in tokenized_sentence:
                if token.text != ",":
                    sentence_list.append(token.text)
            df_step2_2.append({'LabelIdentifier': row['LabelIdentifier'], 'SentenceNumber': sentence_counter, 'sentence': sentence, 'sentence_list': sentence_list, 'locations': locations, })
            sentence_counter += 1  # Increase the sentence number by 1
    if index % 50000 == 0:
        print(index)

# Convert the list of dictionaries to a DataFrame
df_step2_2 = pd.DataFrame(df_step2_1)

#Concatenate together
df_step2 = pd.concat([df_step2_1, df_step2_2], ignore_index=True)

#%% write csv file
df_step2.to_csv("output/datasets/NER_tokenedsentences.csv", index=False, sep=';')

#%% Filter for rows where 'locations' list is not empty
survey_step2_locations = df_step2[df_step2['locations'].apply(lambda x: len(x) > 0)]
survey_step2_nolocations = df_step2[df_step2['locations'].apply(lambda x: len(x) == 0)]

#%%
survey_mette = survey_step2_locations.sample(n=75, random_state=1)
survey_henk = survey_step2_locations.sample(n=75, random_state=2)
survey_myrthe = survey_step2_locations.sample(n=75, random_state=3)
survey_emy = survey_step2_locations.sample(n=75, random_state=4)
survey_yannick = survey_step2_locations.sample(n=75, random_state=5)

#%%
# Sample 75 rows from survey_step2_nolocations
sample_from_nolocations = survey_step2_nolocations.sample(n=75, random_state=1)

# Append the sample to survey_mette
survey_mette = pd.concat([survey_mette, sample_from_nolocations])

# Repeat the process for survey_henk, survey_myrthe, survey_emy, and survey_yannick
sample_from_nolocations = survey_step2_nolocations.sample(n=75, random_state=2)
survey_henk = pd.concat([survey_henk, sample_from_nolocations])

sample_from_nolocations = survey_step2_nolocations.sample(n=75, random_state=3)
survey_myrthe = pd.concat([survey_myrthe, sample_from_nolocations])

sample_from_nolocations = survey_step2_nolocations.sample(n=75, random_state=4)
survey_emy = pd.concat([survey_emy, sample_from_nolocations])

sample_from_nolocations = survey_step2_nolocations.sample(n=75, random_state=5)
survey_yannick = pd.concat([survey_yannick, sample_from_nolocations])


#%% randomize the order
# Randomize the order of rows in survey_mette
survey_mette = survey_mette.sample(frac=1, random_state=42)

# Randomize the order of rows in survey_henk
survey_henk = survey_henk.sample(frac=1, random_state=42)

# Randomize the order of rows in survey_myrthe
survey_myrthe = survey_myrthe.sample(frac=1, random_state=42)

# Randomize the order of rows in survey_emy
survey_emy = survey_emy.sample(frac=1, random_state=42)

# Randomize the order of rows in survey_yannick
survey_yannick = survey_yannick.sample(frac=1, random_state=42)


#%%
survey_mette.to_csv("output/survey_step1/survey_mette.csv", index=False, sep=';')
survey_henk.to_csv("output/survey_step1/survey_henk.csv", index=False, sep=';')
survey_myrthe.to_csv("output/survey_step1/survey_myrthe.csv", index=False, sep=';')
survey_emy.to_csv("output/survey_step1/survey_emy.csv", index=False, sep=';')
survey_yannick.to_csv("output/ssurvey_step1/urvey_yannick.csv", index=False, sep=';')




