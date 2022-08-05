import numpy as np
import queue
import spacy
import time

from re import search
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

nlp = spacy.load("pt_core_news_lg")

INITIAL_QTY_WORDS_TO_GENERATE = 100
INITIAL_SCORE = 500
QTY_WORDS_TO_GET_MEAN = 8
NUMBER_PAST_GAME = 161
MAX_SCORE_DIFFERENCE = 100
MAXIMUM_TENTATIVES = 1500
DRIVER_PATH = r"C:\chromedriver.exe"

INITIAL_WORDS = ["comida", 'local', 'corpo', 'métrica', 'sol', 'ciência', 'animal', 'justiça', 'humano', 'transporte', 'tratamento']

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
xPathTentatives = '//*[@id="root"]/div/div[2]/span[4]'
xPathTentativesAfterWin = '//*[@id="root"]/div/div[5]/span[4]'
xPathGuessedWord = '//*[@id="root"]/div/div[3]/div/div[2]/span[1]' 
xPathGuessedWordAfterWin = '//*[@id="root"]/div/div[6]/div/div[2]/span[1]'
xPathTodayGame = '//*[@id="root"]/div/div[2]/span[2]'
xPathAcceptCookies = '//*[@id="root"]/div/div[5]/div/div[2]/button'

global driver
global inputElement
global haveWonOrGaveUpGame
global startTime
global maximumTentatives

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


def getInputAndSetup(gameNumber, maxTentatives):
  global driver
  global inputElement
  global haveWonOrGaveUpGame
  global startTime
  global maximumTentatives

  maximumTentatives = maxTentatives

  startTime = time.time()

  haveWonOrGaveUpGame = False

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
    getWordScore(word)

  return inputElement


def getSimilarWords(wordsInfo):

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
  global haveWonOrGaveUpGame
  global maximumTentatives

  try:
    inputElement.clear()
    time.sleep(0.1)
    inputElement.send_keys(guessWord)
    time.sleep(0.1)
    inputElement.send_keys(Keys.ENTER)
    time.sleep(0.4)

    guessedWords.add(guessWord)
    guessWord = driver.find_element(By.XPATH, xPathGuessedWord).text
    guessedScore = int(driver.find_element(By.XPATH, xPathGuessedScore).text)
    guessedWords.add(guessWord)
    guessedWordsInfo.put(WordInfo(guessWord, guessedScore))

    numberTentatives = int(driver.find_element(By.XPATH, xPathTentatives).text)
    if(numberTentatives > maximumTentatives):
      haveWonOrGaveUpGame = True

    return guessedScore

  except Exception:
    try:
      guessWord = driver.find_element(By.XPATH, xPathGuessedWordAfterWin).text
      guessedScore = int(driver.find_element(By.XPATH, xPathGuessedScoreAfterWin).text)
      guessedWords.add(guessWord)
      guessedWordsInfo.put(WordInfo(guessWord, guessedScore))

      if(guessedScore == 1):
        haveWonOrGaveUpGame = True
        return guessedScore
    except Exception:
      time.sleep(0.1)
    
    time.sleep(0.1)
    

  return False


def getWordsInfoToGenerateMean():
  wordsInfoToGenerateMean = []
  for _ in range(min(QTY_WORDS_TO_GET_MEAN, len(guessedWordsInfo.queue))):
    wordsInfoToGenerateMean.append(guessedWordsInfo.get())
  
  for wordInfo in wordsInfoToGenerateMean:
    guessedWordsInfo.put(wordInfo)

  
  bestScore = wordsInfoToGenerateMean[0].score
  wordsInfoToGenerateMean = [goi for goi in wordsInfoToGenerateMean if goi.score - bestScore < MAX_SCORE_DIFFERENCE]

  return tuple(wordsInfoToGenerateMean)

def generateAndGuessSimilarWords(toGenerateWordsInfo):
  if toGenerateWordsInfo in processedSetWordsInfo:
    return
  
  similarWords = getSimilarWords(toGenerateWordsInfo)
  processedSetWordsInfo.add(toGenerateWordsInfo)

  for similarWord in similarWords:
    if haveWonOrGaveUpGame:
      break

    getWordScore(similarWord)

    #note: At this point it is possible to have a new word with score less than wordInfo.score, so lets check it at priorityQueue
    newGuessedWordsInfo = getWordsInfoToGenerateMean()
    newSetScore = sum([wi.score for wi in newGuessedWordsInfo])
    currSetScore = sum([wi.score for wi in toGenerateWordsInfo])
    if(newSetScore < currSetScore or len(newGuessedWordsInfo) > len(toGenerateWordsInfo)):
      generateAndGuessSimilarWords(newGuessedWordsInfo)

def playGame(gameNumber = NUMBER_PAST_GAME, maxTentatives = MAXIMUM_TENTATIVES):
  global guessedWordsInfo
  global driver
  
  getInputAndSetup(gameNumber, maxTentatives)

  while haveWonOrGaveUpGame == False:
    toGenerateWordsInfo = getWordsInfoToGenerateMean()
    generateAndGuessSimilarWords(toGenerateWordsInfo)
    guessedWordsInfo.get()

  totalTentatives = None
  try:
    int(driver.find_element(By.XPATH, xPathTentativesAfterWin).text)
  except Exception:
    totalTentatives = MAXIMUM_TENTATIVES

  endTime = time.time()
  totalTime = endTime - startTime
  correctWord = guessedWordsInfo.get().word
  print(gameNumber, totalTentatives, totalTime, correctWord)

  driver.close()
  
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
