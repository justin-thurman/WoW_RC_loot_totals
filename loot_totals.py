#!/usr/bin/env python
# coding: utf-8

import json
import csv
import numpy as np
import datetime as dt
import pandas as pd

with open("items.csv") as f:
	next(f)
	reader = csv.reader(f, skipinitialspace=True)
	items_dict = dict(reader)

df = pd.read_json("export.json")

# Removing rolls that aren't standard loot distributions. For my guild, this included disenchanting and guild banking rolls.
# Update the 'Disenchant' and 'Banking' text strings to reflect the names of rolls you would like to exclude for your guild.
# These lines won't cause any problem if your guild doesn't use these kinds of rolls. You can leave them in place.
df = df[df.response != 'Disenchant']
df = df[df.response != 'Banking']


df["itemID"] = df["itemID"].astype(str)
df["item"] = df["itemID"].map(items_dict) # turning the item column, which contains itemID, into item name

df = df[~df.item.str.contains("Pattern|Formula|Recipe|Schematic|Plans|Tranquilizing")] # removing crafting pattersn and tome of tranq

df.drop(["time", "itemString", "votes", "boss", "isAwardReason", "subType", "equipLoc", "note", "owner", "itemID"], axis=1, inplace=True)

df['player'] = df['player'].map(lambda x: x.split("-")[0]) # removing the realm name after player name


# generating the list of items per date

grouped = df.groupby("date")
drops_db=pd.DataFrame()
drops_db['player'] = list(set(df['player']))
drops_db.set_index("player", inplace=True)

for name, group in grouped: # name is the date, group is the dataframe filtered to that date
    drops_db[f"{name}"] = ""    
    for player in drops_db.index:
        loot = list(group[group['player']==player].item)
        drops_db.at[f"{player}", f"{name}"] = list(loot)
        
drops_db.sort_index(inplace=True)


# generating count of total items received

total_column = []

for player in drops_db.index:
    total = 0
    for date in drops_db.columns:
        total += len(drops_db.loc[player, date])
    total_column.append(total)

drops_db.columns = pd.to_datetime(drops_db.columns).date
drops_db['total'] = total_column

drops_db.to_csv("loot_history.csv")
