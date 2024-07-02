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
from statsmodels.stats.inter_rater import fleiss_kappa
import numpy as np
#%% Set the directory
path = "/Users/Yannick/Documents/Thesis 2024"
os.chdir(path)

#%%load data
results_survey = pd.read_csv("Data/Surveys Step 2/Location Survey.csv", header=None).transpose()
results_survey.drop(results_survey.index[0], inplace=True)

survey_questions = pd.read_csv("output/Survey/survey_sample.csv", delimiter=";")

results_survey.columns = ["Question", "person1", "person2", "person3", "person4"]

pd.concat([survey_questions, results_survey])


#%%
# Set the Question_number based on the condition
results_survey['Question_number'] = results_survey['Question'].apply(
    lambda x: 2 if x == "Welke van de gevonden locaties zijn eigenlijk geen locatie?" else 1
)

#%%

results_survey_for_fleiss = results_survey.drop(columns=["Question_number", "Question"])
for col in results_survey_for_fleiss.columns:
    # Iterate over values in the column
    for idx, val in results_survey_for_fleiss[col].items():
        if isinstance(val, str) and val.isnumeric():
            # If the value is numeric, skip changing it
            continue
        elif val == "Alle locaties zijn correct":
            results_survey_for_fleiss.loc[idx, col] = 0
        else:
            results_survey_for_fleiss.loc[idx, col] = 1

# Convert the entire DataFrame to numerical data type
results_survey_for_fleiss = results_survey_for_fleiss.applymap(pd.to_numeric)


# Get unique categories across all responses
categories = np.unique(results_survey_for_fleiss.values)

# Create a matrix to count how many participants chose each category for each item
matrix = np.zeros((results_survey_for_fleiss.shape[0], len(categories)), dtype=int)

for i in range(results_survey_for_fleiss.shape[0]):  # for each item
    for j, category in enumerate(categories):  # for each category
        matrix[i, j] = np.sum(results_survey_for_fleiss.iloc[i, :] == category)

# Calculate Fleiss' kappa
kappa = fleiss_kappa(matrix, method='fleiss')
print(f"Fleiss' kappa: {kappa}")

#%% Calculate some stats
results_survey_for_stats = pd.concat([results_survey_for_fleiss, results_survey["Question_number"]], axis=1)


#%%
missed_locations = results_survey_for_stats[results_survey_for_stats['Question_number']==1]
wrong_locations = results_survey_for_stats[results_survey_for_stats['Question_number']==2]
missed_locations = missed_locations.drop(columns=["Question_number"])
wrong_locations = wrong_locations.drop(columns=["Question_number"])


# Sum of each column
sums = missed_locations.sum()

# Average of each column
averages = sums.mean()

# Create a new DataFrame to store sums and averages
summary_df = pd.DataFrame({
    'Sum': sums,
    'Average': averages
})

print(summary_df)
#%%


#%%PLot
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







