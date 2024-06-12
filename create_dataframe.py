#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 10:40:16 2024

@author: Yannick
"""
#Load packages
import os
import pandas as pd

#%%set wd
os.chdir("/Users/Yannick/Documents/Thesis 2024")

#%%Load data
files_df = pd.read_csv("Data/files.csv")

#%% Add the index
index_df =  pd.read_csv("index_of_data.csv", sep=";") #Load index data

#Change the labels to strings
index_df['Bestandsnaam van laatste scan'] = index_df['Bestandsnaam van laatste scan'].astype(str)
files_df['LabelIdentifier'] = files_df['LabelIdentifier'].astype(str)

#Make a shorter file number to be used in merging 
index_df['file_number_short'] = index_df['Bestandsnaam van laatste scan'].apply(lambda x: '_'.join(x.split('_')[:-1]))
files_df['file_number_short'] = files_df['LabelIdentifier'].apply(lambda x: '_'.join(x.split('_')[:-1]))

#%% Merge the dataframes
merged_df = pd.merge(index_df, files_df, on='file_number_short', suffixes=('_df1', '_df2'))

# Drop the extra columns
merged_df.drop(columns=['file_number_short'], inplace=True)

#%% Filter the dataframe a little bit
merged_df["space_count"] = merged_df["DocumentContent"].str.count(' ')

# Apply the filter
merged_df = merged_df[(merged_df["space_count"] > 150)] #& (files_df["space_count"] < 1000)]

#%% Save the dataframe to be used in the other scripts
merged_df.to_csv("/Users/Yannick/Documents/Thesis 2024/Data/generale_missiven.csv", index=False)
