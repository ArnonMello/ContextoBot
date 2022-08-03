import queue
import time
from re import search

import numpy as np
import spacy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

nlp = spacy.load("pt_core_news_lg")

INITIAL_QTY_WORDS_TO_GENERATE = 120
INITIAL_SCORE = 500
QTY_WORDS_TO_GET_MEAN = 6
NUMBER_PAST_GAME = 160
MAX_SCORE_DIFFERENCE = 100
DRIVER_PATH = r"C:\chromedriver.exe"

INITIAL_WORDS = ["comida", 'local', 'corpo', 'métrica', 'sol', 'ciência', 'animal', 'justiça', 'humano', 'transporte']

processedSetWordsInfo = set()
guessedWords = set()
guessedWordsInfo = queue.PriorityQueue()

qtyWordsToGenerate = INITIAL_QTY_WORDS_TO_GENERATE
currentScore = INITIAL_SCORE

xPathOptions = '//*[@id="root"]/div/div[1]/div[2]/button'
xPathPastGames = '//*[@id="root"]/div/div[1]/div[2]/div[2]/button[4]'
xPathInput = '//*[@id="root"]/div/form/input'
xPathGuessedScore = '//*[@id="root"]/div/div[3]/div/div[2]/span[2]'
xPathGuessedScoreAfterWin = '//*[@id="root"]/div/div[6]/div/div[2]/span[2]'
xPathTentativesAfterWin = '//*[@id="root"]/div/div[5]/span[4]'
xPathGuessedWord = '//*[@id="root"]/div/div[3]/div/div[2]/span[1]' 
xPathGuessedWordAfterWin = '//*[@id="root"]/div/div[6]/div/div[2]/span[1]'
xPathTodayGame = '//*[@id="root"]/div/div[2]/span[2]'
xPathAcceptCookies = '//*[@id="root"]/div/div[5]/div/div[2]/button'

global driver
global inputElement
global haveWonGame
global startTime

class WordInfo:
  def __init__(self, word, score):
    self.word = word
    self.score = score
  
  def __lt__(self, other):
    if self.score == other.score:
      return self.word < other.word

    return self.score < other.score

class gameInfo:
  def __init__(self, gameNumber, numberTentatives, totalTime, correctWord):
    self.gameNumber = gameNumber
    self.numberTentatives = numberTentatives
    self.totalTime = totalTime
    self.correctWord = correctWord

def getXPathPastGame(number):
  return str('//*[@id="root"]/div/div[5]/div/div[2]/div/div/div[{}]/button').format(number)


def clickAndWaitXPath(xPath):
  global driver
  try:
    element = driver.find_element(By.XPATH, xPath)
    time.sleep(0.2)
    element.click()
    time.sleep(0.2)
    return element
  except Exception:
    time.sleep(0.2)

  return False


def getInputAndSetup(gameNumber):
  global driver
  global inputElement
  global haveWonGame
  global startTime

  startTime = time.time()

  haveWonGame = False

  processedSetWordsInfo.clear()
  guessedWords.clear()
  guessedWordsInfo.queue.clear()

  driver = webdriver.Chrome(DRIVER_PATH)
  driver.get('https://contexto.me/')
  time.sleep(5)

  clickAndWaitXPath(xPathAcceptCookies)
  clickAndWaitXPath(xPathOptions)
  clickAndWaitXPath(xPathPastGames)

  todayGame = driver.find_element(By.XPATH, xPathTodayGame).text
  todayGame = int(todayGame.replace('#', ''))
  numberToPastGame = 1 if gameNumber == 0 else todayGame - gameNumber + 1

  while clickAndWaitXPath(getXPathPastGame(numberToPastGame)) == False:
    time.sleep(0.2)
  
  inputElement = driver.find_element(By.XPATH, xPathInput)
  time.sleep(2)

  for word in INITIAL_WORDS:
    score = getWordScore(word)
    # wordInfo = WordInfo(word, score)
    # guessedWordsInfo.put(wordInfo)

  return inputElement


def getSimilarWords(wordsInfo):
  # if(qtyWordsToGenerate == 0):
  #   return []

  # qtyWordsToGenerate = min(300, max(10, int(15000/(wordsInfo[0].score))))

  size = len(nlp(wordsInfo[0].word).vector)
  meanVector = [np.zeros((size))]
  totalWeight = 0
  #todo:use statistics.mean
  for wordInfo in wordsInfo:
    weight = 500/wordInfo.score
    totalWeight += weight
    vector = nlp(wordInfo.word).vector
    meanVector += (vector*weight)
  meanVector = np.array(meanVector/totalWeight)

  ms = nlp.vocab.vectors.most_similar(meanVector, n=qtyWordsToGenerate)
  words = [nlp.vocab.strings[w] for w in ms [0][0]]
  words = [w for w in words if not search('-', str(w))]
  return words


def getWordScore(guessWord):
  if(guessWord in guessedWords):
    return
  
  global inputElement
  global driver
  global haveWonGame

  inputElement.clear()
  time.sleep(0.1)
  inputElement.send_keys(guessWord)
  time.sleep(0.1)
  inputElement.send_keys(Keys.ENTER)
  time.sleep(0.4)
  guessedWords.add(guessWord)

 

  try:
    guessWord = driver.find_element(By.XPATH, xPathGuessedWord).text
    guessedScore = int(driver.find_element(By.XPATH, xPathGuessedScore).text)
    guessedWords.add(guessWord)
    guessedWordsInfo.put(WordInfo(guessWord, guessedScore))

    return guessedScore

  except Exception:
    try:
      guessWord = driver.find_element(By.XPATH, xPathGuessedWordAfterWin).text
      guessedScore = int(driver.find_element(By.XPATH, xPathGuessedScoreAfterWin).text)
      guessedWords.add(guessWord)
      guessedWordsInfo.put(WordInfo(guessWord, guessedScore))

      if(guessedScore == 1):
        haveWonGame = True
        return guessedScore
    except Exception as e:
      #print(e)
      time.sleep(0.1)
    
    time.sleep(0.1)
    

  return False


def getWordsInfoToGenerateMean():
  wordsInfoToGenerateMean = []
  for i in range(min(QTY_WORDS_TO_GET_MEAN, len(guessedWordsInfo.queue))):
    wordsInfoToGenerateMean.append(guessedWordsInfo.get())
  
  for wordInfo in wordsInfoToGenerateMean:
    guessedWordsInfo.put(wordInfo)

  
  bestScore = wordsInfoToGenerateMean[0].score
  wordsInfoToGenerateMean = [goi for goi in wordsInfoToGenerateMean if goi.score - bestScore < MAX_SCORE_DIFFERENCE]

  return tuple(wordsInfoToGenerateMean)

def generateAndGuessSimilarWords(toGenerateWordsInfo):
  if toGenerateWordsInfo in processedSetWordsInfo:
    return
  
  # qtyWordsToGenerate = min(100, max(1, int(10000/(toGenerateWordsInfo.score))))
  similarWords = getSimilarWords(toGenerateWordsInfo)
  processedSetWordsInfo.add(toGenerateWordsInfo)

  for similarWord in similarWords:
    if haveWonGame:
      break

    getWordScore(similarWord)

    #note: At this point it is possible to have a new word with score less than wordInfo.score, so lets check it at priorityQueue
    newGuessedWordsInfo = getWordsInfoToGenerateMean()
    newSetScore = sum([wi.score for wi in newGuessedWordsInfo])
    currSetScore = sum([wi.score for wi in toGenerateWordsInfo])
    if(newSetScore < currSetScore or len(newGuessedWordsInfo) > len(toGenerateWordsInfo)):
      # guessedWordsInfo.get()
      generateAndGuessSimilarWords(newGuessedWordsInfo)

def playGame(gameNumber = NUMBER_PAST_GAME):
  global guessedWordsInfo
  
  getInputAndSetup(gameNumber)

  while haveWonGame == False:
    toGenerateWordsInfo = getWordsInfoToGenerateMean()
    generateAndGuessSimilarWords(toGenerateWordsInfo)
    guessedWordsInfo.get()

  totalTentatives = int(driver.find_element(By.XPATH, xPathTentativesAfterWin).text)

  endTime = time.time()
  totalTime = endTime - startTime
  correctWord = guessedWordsInfo.get().word
  print(gameNumber, totalTentatives, totalTime, correctWord)
  
  return gameInfo(gameNumber, totalTentatives, totalTime, correctWord)
    
def main():   
  records = open("records.txt", 'w')
  records.write('gameNumber NumberTentatives totalTime correctWord\n')

  for i in reversed(range(NUMBER_PAST_GAME+1)):
    records = open("records.txt", 'a')
    gameInfo = playGame(i)
    records.write('{} {} {} {}\n'.format(gameInfo.gameNumber, gameInfo.numberTentatives, gameInfo.totalTime, gameInfo.correctWord))
    records.close()

if __name__ == "__main__":
  main()
