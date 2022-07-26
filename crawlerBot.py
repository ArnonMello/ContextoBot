import time
from re import search

import numpy as np
import spacy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

PATH = "C:\chromedriver.exe"
nlp = spacy.load("pt_core_news_lg")

randomWords = ["cor", "flor", "fruta", "luz", "vida", "família", "computador", "memória", "sol", "rocha", "mente", "aceitar", "ganhar", "loucura", "pessoa", "cabelo", "matemática", "língua"]
triedWords = set()
guessedWords = set()
qtyWords = 20
currentScore = 100

driver = webdriver.Chrome(PATH)
driver.get('https://contexto.me/')
time.sleep(2)

def setup():
  options = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/div[2]/button')
  time.sleep(0.3)
  options.click()
  time.sleep(0.3)
  pastGames = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/div[2]/div[2]/button[4]')
  time.sleep(0.3)
  pastGames.click()
  time.sleep(0.3)
  oldGame = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[5]/div/div[2]/div/div/div[4]/button')
  time.sleep(0.3)
  oldGame.click()
  time.sleep(0.3)
  inputElement = driver.find_element(By.XPATH, '//*[@id="root"]/div/form/input')
  time.sleep(2)
  tryGuessWords(inputElement, randomWords)
  return inputElement


def getSimilarWords(word):
  if(qtyWords == 0):
    return []
  ms = nlp.vocab.vectors.most_similar(
    np.asarray([nlp.vocab.vectors[nlp.vocab.strings[word]]]), n=qtyWords)
  words = [nlp.vocab.strings[w] for w in ms[0][0]]
  words = [w for w in words if not search('-', str(w))]
  return words


def getNextWord():
  tentatives = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/span[4]')
  tentatives = int(tentatives.text)
  try:
    for row in range(1, tentatives+1):
      xPath = '//*[@id="root"]/div/div[4]/div[{}]/div[2]'.format(row)
      rowData = driver.find_element(By.XPATH, xPath).text
      wordInRow = rowData[:rowData.find("\n")]
      rowScore = rowData[rowData.find("\n"):]
      global qtyWords
      qtyWords = int(10*min(20, int(1000/int(rowScore))))
      if wordInRow not in triedWords:
        global currentScore
        currentScore = int(rowScore)
        triedWords.add(wordInRow)
        return wordInRow
  except Exception as e:
    print(e)

def tryGuessWords(inputElement, wordList):
  for guessWord in wordList:
      if(guessWord in guessedWords):
        continue
      inputElement.clear()
      time.sleep(0.1)
      inputElement.send_keys(guessWord)
      time.sleep(0.1)
      inputElement.send_keys(Keys.ENTER)
      time.sleep(0.4)
      try:
        guessedScore = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div[2]/span[2]').text
        #//*[@id="root"]/div/div[3]/div/div[2]/span[2]
        global currentScore
        if int(guessedScore) < currentScore:
          pastScore = currentScore
          currentScore = int(guessedScore)
          wordListNew = getSimilarWords(guessWord)
          tryGuessWords(inputElement, wordListNew)
          triedWords.add(guessWord)
          currentScore = pastScore
      except Exception as e:
        time.sleep(0.1)

    
def main(): 
  inputElement = setup()
  while True:
    word = getNextWord()
    wordList = getSimilarWords(word)
    tryGuessWords(inputElement, wordList)

  time.sleep(1000)

main()
