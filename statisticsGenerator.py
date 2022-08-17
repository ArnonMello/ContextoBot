import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statistics

COLUMNS_NAMES = ['gameNumber', 'numberTentatives', 'totalTime', 'correctWord']

def main():
  records = pd.read_csv('records.csv')
  allTentatives = records.loc[:, 'numberTentatives']
  allSucessfulTentatives = [v for v in allTentatives if v < 1500]

  fig, (ax1, ax2) = plt.subplots(1, 2)
  
  bins= np.linspace(0, 1000, 11, dtype = int)
  ax1.hist(allSucessfulTentatives, bins=bins, edgecolor="k")
  ax1.set(xlabel = 'Number of Tentatives', ylabel = 'Quantity of Games')
  meanTentatives = statistics.mean(allSucessfulTentatives)
  ax1.axvline(meanTentatives, color='k', linestyle='dashed', linewidth=1, label = 'Mean Tentatives')
  ax1.legend()

  print('All sucessful games: {}\nAll games {}'.format(len(allSucessfulTentatives), len(allTentatives)))
  print('Mean tentatives: {}'.format(meanTentatives))

  totalSucessfulTimes = records.loc[records['numberTentatives'] < 1500]
  totalSucessfulTimes = totalSucessfulTimes['totalTime']
  
  bins= np.linspace(0, totalSucessfulTimes.max()+1, 15, dtype = int)
  ax2.hist(totalSucessfulTimes, bins=bins, edgecolor="k")
  ax2.set(xlabel = 'Total Time Seconds', ylabel = 'Quantity of Games')
  meanTime = totalSucessfulTimes.mean()
  ax2.axvline(meanTime, color='k', linestyle='dashed', linewidth=1, label = 'Mean Time')
  ax2.legend()
  
  print('Mean time: {}'.format(meanTime))

  plt.show()

if __name__ == "__main__":
  main()