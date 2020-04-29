#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import csv
import numpy as np
import datetime as dt
import pandas as pd

def player_loot(name):
	loot = []
	for drop in data:
		if name.title() in drop["player"] and not drop["response"] == "Disenchant":
			loot.append(items_dict[str(drop["itemID"])])
	loot.sort()
	return(f"{name.title()} has received {len(loot)} items.", loot)

def class_average_loot(name):
	roster = []
	player_class = ""
	for drop in data:
		if name.title() in drop["player"]:
			player_class=drop["class"]
			break
	for drop in data:
		if drop["class"]==player_class and (drop["player"].split("-")[0]).lower() in raiders and not drop["response"] == "Disenchant":
			roster.append(drop["player"])
	total_items_for_class=len(roster)
	number_of_class=len(set(roster))
	return total_items_for_class/number_of_class


class Member:
	def __init__(self, name):
		self.name=name
		self.items=["test_item"]

raiders = ["ariadnye", "fawyn", "floramel", "mav", "zallai", "aimelia", "evindel", "steadyshot", "tower", "fiz", "rancelor",
		   "relink", "sessnishi", "exaethian", "gildi", "gordy", "kyra", "payge", "violily", "yungdingo", "bubblywrap", "elluna",
		   "hitomi", "holymedic", "skorgson", "spri", "lumberfoot", "mackdagger", "noxxious", "nyhthraefn", "theodora", "vihgo",
		   "akku", "hiriko", "jank", "kaydra", "kylace", "xilus", "alunys", "benecia", "caritheri", "gossow", "meadowglen",
		   "myrd", "sanno", "xandin"]
data = json.load(open("export.json", "r"))

with open("items.csv") as f:
	next(f)
	reader = csv.reader(f, skipinitialspace=True)
	items_dict = dict(reader)


# In[2]:


df = pd.read_json("export.json")


# In[3]:


df = df[df.response != 'Disenchant'] # removing disenchanting and banking rolls
df = df[df.response != 'Banking']


# In[4]:


df["itemID"] = df["itemID"].astype(str)
df["item"] = df["itemID"].map(items_dict) # turning the item column, which contains itemID, into item name


# In[5]:


df = df[~df.item.str.contains("Pattern|Formula|Recipe|Schematic|Plans|Tranquilizing")] # removing crafting pattersn and tome of tranq


# In[6]:


df.drop(["time", "itemString", "votes", "boss", "isAwardReason", "subType", "equipLoc", "note", "owner", "itemID"], axis=1, inplace=True)


# In[7]:


df['player'] = df['player'].map(lambda x: x.split("-")[0]) # removing the realm name after player name


# In[8]:


grouped = df.groupby("date")


# In[9]:


# generating the list of items per date

drops_db=pd.DataFrame()
drops_db['player'] = list(set(df['player']))
drops_db.set_index("player", inplace=True)

for name, group in grouped: # name is the date, group is the dataframe filtered to that date
    drops_db[f"{name}"] = ""    
    for player in drops_db.index:
        loot = list(group[group['player']==player].item)
        drops_db.at[f"{player}", f"{name}"] = list(loot)
        
drops_db.sort_index(inplace=True)


# In[10]:


# generating count of total items received
total_column = []

for player in drops_db.index:
    total = 0
    for date in drops_db.columns:
        total += len(drops_db.loc[player, date])
    total_column.append(total)

drops_db.columns = pd.to_datetime(drops_db.columns).date
drops_db['total'] = total_column


# In[11]:


drops_db.to_csv("remnant_loot.csv")

