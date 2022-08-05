import pandas as pd
import os.path

from crawlerBot import playGame

CURRENT_GAME = 162
PATH_TO_DATAFRAME = 'C:/Users/arnon/Documents/IME/ContextoBot/records.csv'
COLUMNS_NAMES = ['gameNumber', 'numberTentatives', 'totalTime', 'correctWord']
MAX_TENTATIVES = 1000

def main():
  recordsExists = os.path.exists(PATH_TO_DATAFRAME)
  records = pd.DataFrame()
  if recordsExists:
    records = pd.read_csv('records.csv')
  else:
    records = pd.DataFrame(columns=COLUMNS_NAMES)

  for gameNumber in range(len(records) + 1, CURRENT_GAME + 1):
    gameInfo = playGame(gameNumber, MAX_TENTATIVES)
    record = pd.DataFrame([(gameInfo.gameNumber, gameInfo.numberTentatives, gameInfo.totalTime, gameInfo.correctWord)], columns = COLUMNS_NAMES)
    records = pd.concat([records, record])
    records.to_csv('records.csv', index = False)
 
if __name__ == "__main__":
  main()