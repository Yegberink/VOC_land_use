#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 10:44:35 2024

@author: Yannick
"""

#%%Load packages
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
#%% Set the directory
path = "/Users/Yannick/Documents/Thesis 2024"
os.chdir(path)


#%%Load data

#Trade datasets
cargo_1 = pd.read_excel("Data/trade_data/cargos (1).xls", "cargo", header=None)
cargo_2 = pd.read_excel("Data/trade_data/cargos (2).xls", "cargo", header=None)
cargo_3 = pd.read_excel("Data/trade_data/cargos (3).xls", "cargo", header=None)

#weight conversions
weight_conversion = pd.read_csv("Data/conversion_weights1.csv")


#%% clean the data
#Concat into single df
trade_data = pd.concat([cargo_1, cargo_2, cargo_3])

#Select first 8 columns
trade_data = trade_data.iloc[:,0:8]

#Name these columns
trade_data.columns = ["book_year", "quantity", "unit", "product", "departure_place", "departure_region", "arrival_place", "arrival_region"]

#Convert - to NAN
trade_data.replace('-', None, inplace=True)

#%%Extract a single year so it can be ordered
trade_data["year"] = trade_data["book_year"].str[:4].astype(int)
trade_data = trade_data.sort_values(by='year')

#%% Convert the quantities to the english format and convert to numeric
trade_data["quantity"] = trade_data["quantity"].str.replace('.', '') #Remove the thousand separators
trade_data["quantity"] = trade_data["quantity"].str.replace(',', '.') #Replace the , with a .
trade_data["quantity"] = pd.to_numeric(trade_data["quantity"]) #Make numeric

#%%Convert similar products to the same sort

#manual input of the different names for commodities based on VOC glossarium
kaneel = ["kaneel", "boskaneel", "kaneel de matte", "candela"]
zijde = ["zijde", "ablako", "agoni", "ardasse", "ardassina", "armozijn", "baa", "bariga", "bogy", "cabessa", "cannagy", "capitoen", "casagy", "chauls", "coetchiaal", "cora", "dom", "floretzijde", "floszijde", "fora", "gangali", "gasen", "gert-kerckerie", "hittou", "kannegie", "kedgoda pessend", "ketsier", "khan baffy", "legia", "matiaal", "moghta", "mongo", "pangia", "parelzijde", "patteni", "pee", "peling", "poilzijde", "poolzijde", "poilzijde", "potti", "quetchoda-passant", "selvatica", "serge", "sjesum", "tabijnen", "taffachelas", "tafta", "tamut", "tanna-banna", "tanny", "tantianozijde", "thujas", "vloszijde", "volte corte", "zeem"]
peper = ["peper", "staartpeper", "cubebe", "piper cubebe", "ruagiepeper"]
nootmuskaat = ["nootmuskaat", "muskaatnoten", "brouwersnoten", "foelienoten", "foelie", "rompen"]
kruidnagel = ["antoffel", "blom", "caplet", "garioffelnagel", "nagel", "kruidnagel"]
thee = ["thee", "bing", "boei", "congo", "joosjesthee", "pecco", "songlo", "souchong", "tscha"]
koffie = ["koffie", "bun", "cauwa", "kauwa", "kitscha"]
suiker = ["suiker", "gula", "jagersuycker", "jagru", "poeyer", "stoksuiker", "kandijsuiker", "tamarinde"]
opium = ["amfioen", "opium"]

#initiate product category
trade_data["product_category"] = None

#Set the product category to the overarching name based on previous lists and translate to english
trade_data.loc[trade_data["product"].isin(kaneel), "product_category"] = "Cinnamon"
trade_data.loc[trade_data["product"].isin(zijde), "product_category"] = "Silk"
trade_data.loc[trade_data["product"].isin(peper), "product_category"] = "Pepper"
trade_data.loc[trade_data["product"].isin(nootmuskaat), "product_category"] = "Nutmeg"
trade_data.loc[trade_data["product"].isin(kruidnagel), "product_category"] = "Cloves"
trade_data.loc[trade_data["product"].isin(thee), "product_category"] = "Tea"
trade_data.loc[trade_data["product"].isin(koffie), "product_category"] = "Coffee"
trade_data.loc[trade_data["product"].isin(suiker), "product_category"] = "Sugar"
trade_data.loc[trade_data["product"].isin(opium), "product_category"] = "Opium"

    
#%% Filter for the products

#Create the list of commodities
commodities = ["Silk", "Pepper", "Cinnamon", "Nutmeg", "Cloves", "Tea", "Coffee", "Sugar", "Opium"]
#Initiate empty dataframe
conversion_commodities = pd.DataFrame()

#Loop over the commidites in the list
for commodity in commodities:
    #Filter for one of the commodities
    filtered_trade_data = trade_data[(trade_data["product_category"] == commodity)]
    
    #Filter the conversion weights
    filtered_weight_conversions = weight_conversion[weight_conversion["commodity"] == commodity]
    
    #Merge these two dataframes
    merged_data = pd.merge(filtered_trade_data, filtered_weight_conversions)
    
    #Concatinate the newly merged dataframe with the conversion commodities df
    conversion_commodities = pd.concat([conversion_commodities, merged_data])
    print(commodity + ":")
    print(len(merged_data)/len(filtered_trade_data)*100)
    
#Calculate the weight of the commodities in kg
conversion_commodities["weight_kg"] = conversion_commodities["quantity"] * conversion_commodities["conversion"]

#Clean the trade data to keep only the interesting columns
cleaned_trade_data = conversion_commodities[["year", "weight_kg", "product_category", "departure_place", "departure_region", "arrival_place", "arrival_region"]]

cleaned_trade_data.to_csv("output/datasets/cleaned_trade_data.csv", index=False)

#%% Ceylon

# Filter data for Ceylon
Ceylon_trade = cleaned_trade_data[cleaned_trade_data["departure_region"] == "Ceylon"]

# Group by product category and year, then sum the weights
Ceylon_trade_grouped = Ceylon_trade.groupby(['product_category', 'year']).sum().reset_index()

# Pivot the table to have years on the x-axis and product categories as columns
pivot_table = Ceylon_trade_grouped.pivot(index='year', columns='product_category', values='weight_kg')

# Plot the data
plt.figure(figsize=(9, 6))
for column in pivot_table.columns:
    plt.plot(pivot_table.index, pivot_table[column], label=column)

plt.xlabel('Year')
plt.ylabel('Weight (kg)')
plt.legend(title='Product Category')

plt.savefig('output/trade_Ceylon.png', dpi=300)
plt.show()

#%%Calculate total cinnamon trade ceylon between 1700 and 1760

Ceylon_trade_cinnamon = Ceylon_trade[Ceylon_trade["product_category"]=="Cinnamon"]

Ceylon_trade_cinnamon_years = Ceylon_trade_cinnamon[
    (Ceylon_trade_cinnamon["year"] >= 1700) & 
    (Ceylon_trade_cinnamon["year"] <= 1760)
]

weight_tonne_cinnamon = Ceylon_trade_cinnamon_years["weight"].sum()/10000

#%%Create plots

#group the data and sum by product and year
grouped_data = cleaned_trade_data.groupby(["year", "product_category"], as_index=False).sum()[["year", "product_category", "weight_kg"]]

grouped_data["1000tonnes"] = grouped_data['weight_kg'] / 1000000

commodities2 = ["Nutmeg", "Cinnamon", "Cloves"]

# Create 3 subplots
fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10, 9), sharex=False, sharey=False)

# Flatten the axes array for easier iteration
axes = axes.flatten()

# Iterate over commodities and plot each one
for i, commodity in enumerate(commodities2):
    # Filter data for the current commodity
    commodity_data = grouped_data[grouped_data["product_category"] == commodity]
    
    # Plot quantity over time
    sns.lineplot(x="year", y="1000tonnes", data=commodity_data, ax=axes[i])
    
    # Perform linear regression to add a trend line
    X = commodity_data["year"].values.reshape(-1, 1)
    y = commodity_data["1000tonnes"].values.reshape(-1, 1)
    linear_regressor = np.polyfit(X.flatten(), y.flatten(), 1)
    trend_line = np.poly1d(linear_regressor)
    
    # Plot trend line
    axes[i].plot(commodity_data["year"], trend_line(commodity_data["year"]), color='red', linestyle='--')
    
    # Calculate R^2 value
    y_pred = trend_line(commodity_data["year"])
    ss_res = np.sum((y.flatten() - y_pred)**2)
    ss_tot = np.sum((y.flatten() - np.mean(y.flatten()))**2)
    r2 = 1 - (ss_res / ss_tot)
    
    # Annotate R^2 value on the plot
    axes[i].text(0.05, 0.95, f'$R^2$ = {r2:.2f}', transform=axes[i].transAxes, fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
    
    # Set title for each subplot
    axes[i].set_title(commodity)
    
    # Set individual y-axis scale for each subplot
    axes[i].set_ylim(0, (commodity_data["1000tonnes"].max() + commodity_data["1000tonnes"].max() * 0.1))
    axes[i].set_xlabel("Year")
    axes[i].set_ylabel("Weight (ktonnes)")

# Adjust layout and display the plot
plt.tight_layout()

# First save the plot as png
plt.savefig('output/commodity_plots_with_trendline.png', dpi=300)

# Then show the plot
plt.show()

#%% Do the same but then with rigid axis


# Create subplots
fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(15, 10), sharex=True, sharey=True)

# Flatten the axes array for easier iteration
axes = axes.flatten()

# Iterate over commodities and plot each one
for i, commodity in enumerate(commodities):
    # Filter data for the current commodity
    commodity_data = grouped_data[grouped_data["product_category"] == commodity]
    
    # Plot quantity over time
    sns.lineplot(x="year", y="1000tonnes", data=commodity_data, ax=axes[i])
    
    # Set title for each subplot
    axes[i].set_title(commodity)
    axes[i].set_ylabel("Weight (ktonnes)")

# Adjust layout and display the plot
plt.tight_layout()
plt.savefig('output/commodity_plots_rigid_axis.png', dpi=300)
plt.show()



