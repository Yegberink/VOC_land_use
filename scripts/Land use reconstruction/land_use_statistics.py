#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 11:29:34 2024

@author: Yannick
"""

#%% Load packages
import pandas as pd
import os
import matplotlib.pyplot as plt

#%% Set the directory
path = "/Users/Yannick/Documents/Thesis 2024"
os.chdir(path)

#%%Load data

georeferenced_areas = pd.read_excel("output/datasets/georeferenced_text_locations.xlsx")
total_areas = pd.read_excel("output/datasets/Dataset_ceylon_1723.xlsx", sheet_name="areas")
polygons_data = pd.read_excel("output/datasets/polygons_data.xlsx")


georeferenced_areas.columns = ["geometry", "fid", "id", "Year", "Village", "Region1", "Region2", "Total AM", "Total corni", "Cultivated AM", "Cultivated corni", "hectares_total", "hectares_cultivated", "remarks"]
total_areas.columns = ["id", "Year", "Village", "Region1", "Region2", "Total AM", "Total corni", "Cultivated AM", "Cultivated corni", "hectares_total", "hectares_cultivated", "remarks", "coding"]

#%%compute some statistics
georeferenced_total = georeferenced_areas["hectares_total"].sum()
all_areas_total = total_areas["hectares_total"].sum()

hina_alloetcoer = total_areas[
    (total_areas["Region2"] == "Hina Corle") |  
    (total_areas["Region2"] == "Aloetcoer Corle")
]

hina_alloetcoer_total = hina_alloetcoer["hectares_total"].sum()
georeferenced_cultivated = georeferenced_areas["hectares_cultivated"].sum()
all_areas_cultivated = total_areas["hectares_cultivated"].sum()

total_areas["difference"] = total_areas["hectares_total"] - total_areas["hectares_cultivated"]

consent_area = total_areas[
    (total_areas["remarks"] != "Is cultivated without consent, the land is poor") & 
    (total_areas["remarks"] != "Is cultivated without consent")
]


no_consent_area = total_areas[
    (total_areas["remarks"] == "Is cultivated without consent, the land is poor") |  
    (total_areas["remarks"] == "Is cultivated without consent")
]

no_consent_total_area = no_consent_area["hectares_total"].sum()
consent_total_area = consent_area["hectares_total"].sum()

hina_alloetcoer_cultivated = hina_alloetcoer["hectares_cultivated"].sum()



#Print some interesting things:
print("Percentage georeferenced of the total area:")
print(georeferenced_total/all_areas_total*100)
print("")
print("Percentage georeferenced of the cultivated area:")
print(georeferenced_cultivated/all_areas_cultivated*100)
print("")
print("Percentage georeferenced of the total area hina, alloetcoer:")
print(georeferenced_total/hina_alloetcoer_total*100)
print("")
print("Percentage georeferenced of the cultivated area hina, alloetcoer:")
print(georeferenced_cultivated/hina_alloetcoer_cultivated*100)
print("")
print("Percentage of area no longer cultivated:")
print(total_areas["difference"].sum()/all_areas_total*100)

#%%Qualitative assessment 
coding_values = total_areas["coding"].value_counts().reset_index()

#%%Land use polygons

total_land_use_polygons = polygons_data.groupby("land_use").sum().reset_index()
total_land_use_polygons.drop(columns=["wkt_geom", "fid", "layer"], inplace=True)

#%%

# Plotting the bar chart
plt.figure(figsize=(10, 6))
plt.bar(total_land_use_polygons["land_use"], total_land_use_polygons["area"]/10000) # replace "some_value_column" with the column you want to plot

# Adding labels and title
plt.xlabel("Land Use")
plt.ylabel("Total land area (ha)")
plt.title("Total Land Use Polygons")

# Rotating x labels for better readability
plt.xticks(rotation=45)

# Display the plot
plt.tight_layout()
plt.show()







