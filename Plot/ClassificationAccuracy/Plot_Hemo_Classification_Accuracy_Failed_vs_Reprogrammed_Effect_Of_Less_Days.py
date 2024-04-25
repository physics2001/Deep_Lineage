# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 22:13:33 2022

@author: zhang
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

Days = ['Day2', 'Day4', 'Day6']
dfs = []

dfs.append(pd.read_csv('Results/Classification_Mon_Neu_Without_Day4_and_Day6_Result.csv', index_col=0))

dfs.append(pd.read_csv('Results/Classification_Mon_Neu_Without_Day6_Result.csv', index_col=0))

dfs.append(pd.read_csv('Results/Classification_Mon_Neu_Result.csv', index_col=0))

for i in range(len(Days)): 
    dfs[i] = dfs[i].loc[(dfs[i]['Classification_Dropout'] == 0.25)]

for i in range(len(Days)): 
    dfs[i]['time'] = [i] * 6

df = pd.concat(dfs, axis=0)

# Plot the responses for different events and regions
# plt.clf()
plt.figure(figsize=(12,7.5))
ax1 = sns.lineplot(x="time", y="Accuracy", marker='.', markersize=16,
                   color='r', label='accuracy',
             # hue="region", style="event", 
             data=df)
ax1.set_xticks(list(range(len(Days))))
ax1.set_xticklabels(Days)
ax2 = plt.twinx()
ax2 = sns.lineplot(x="time", y="Categorical_Crossentropy", marker='^', markersize=10,
                   color='b', label='crossentropy',
             # hue="region", style="event",
             data=df, ax=ax2)
ax2.set_xticks(list(range(len(Days))))
ax2.set_xticklabels(Days)
ax1.legend(loc='center left')
ax2.legend(loc='center right')
ax1.set_ylabel('Accuracy')
ax2.set_ylabel('Crossentropy')
ax1.set_xlabel('Classification with Time Series Data That Ends On')
plt.title('Differences in Classification Accuracy and Crossentropy With Limited Hematopoiesis Time Series Data')
plt.savefig('Plots/Differences in Classification Accuracy and Crossentropy With Limited Hematopoiesis Time Series Data.png')
plt.savefig('Plots/pdfs/Differences in Classification Accuracy and Crossentropy With Limited Hematopoiesis Time Series Data.pdf')


