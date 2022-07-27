import queue
import time
from re import search

import numpy as np
import spacy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

nlp = spacy.load("pt_core_news_lg")

INITIAL_QTY_WORDS_TO_GENERATE = 20
INITIAL_SCORE = 500
NUMBER_PAST_GAME = 5
DRIVER_PATH = r"C:\chromedriver.exe"

INITIAL_WORDS = ["cor", "flor", "fruta", "luz", "vida", "família", "computador", "memória", "sol", "rocha", "mente", "aceitar", "ganhar", "loucura", "pessoa", "cabelo", "matemática", "língua"]

processedWords = set()
guessedWords = set()
wordsToProcess = queue.PriorityQueue()

qtyWordsToGenerate = INITIAL_QTY_WORDS_TO_GENERATE
currentScore = INITIAL_SCORE

xPathOptions = '//*[@id="root"]/div/div[1]/div[2]/button'
xPathPastGames = '//*[@id="root"]/div/div[1]/div[2]/div[2]/button[4]'
xPathInput = '//*[@id="root"]/div/form/input'
xPathGuessedScore = '//*[@id="root"]/div/div[3]/div/div[2]/span[2]'
xPathTentatives = '//*[@id="root"]/div/div[2]/span[4]'

global driver
global inputElement


class WordInfo:
  def __init__(self, word, score):
    self.word = word
    self.score = score
  
  def __lt__(self, other):
    if self.score == other.score:
      return self.word < other.word

    return self.score < other.score

def getXPathPastGame(number):
  return str('//*[@id="root"]/div/div[5]/div/div[2]/div/div/div[{}]/button').format(number)


def clickAndWaitXPath(xPath):
  global driver
  element = driver.find_element(By.XPATH, xPath)
  time.sleep(0.2)
  element.click()
  time.sleep(0.2)
  return element


def getInputAndSetup():
  global driver
  global inputElement

  driver = webdriver.Chrome(DRIVER_PATH)
  driver.get('https://contexto.me/')
  time.sleep(2)

  clickAndWaitXPath(xPathOptions)
  clickAndWaitXPath(xPathPastGames)
  clickAndWaitXPath(getXPathPastGame(NUMBER_PAST_GAME))
  inputElement = driver.find_element(By.XPATH, xPathInput)
  time.sleep(2)

  for word in INITIAL_WORDS:
    score = getWordScore(word)
    wordInfo = WordInfo(word, score)
    wordsToProcess.put(wordInfo)

  return inputElement


def getSimilarWords(word, qtyWordsToGenerate = INITIAL_QTY_WORDS_TO_GENERATE):
  if(qtyWordsToGenerate == 0):
    return []
  ms = nlp.vocab.vectors.most_similar(np.asarray([nlp.vocab.vectors[nlp.vocab.strings[word]]]), n=qtyWordsToGenerate)
  words = [nlp.vocab.strings[w] for w in ms [0][0]]
  words = [w for w in words if not search('-', str(w))]
  return words


def getWordScore(guessWord):
  if(guessWord in guessedWords):
    return
  
  global inputElement
  inputElement.clear()
  time.sleep(0.1)
  inputElement.send_keys(guessWord)
  time.sleep(0.1)
  inputElement.send_keys(Keys.ENTER)
  time.sleep(0.4)
  guessedWords.add(guessWord)

  try:
    guessedScore = int(driver.find_element(By.XPATH, xPathGuessedScore).text)
    wordsToProcess.put(WordInfo(guessWord, guessedScore))
    return guessedScore

  except Exception:
    time.sleep(0.1)

  return False


def generateAndGuessSimilarWords(wordInfo):
  if wordInfo.word in processedWords:
    return
  
  qtyWordsToGenerate = min(100, max(1, int(10000/(wordInfo.score))))
  similarWords = getSimilarWords(wordInfo.word, qtyWordsToGenerate)
  processedWords.add(wordInfo.word)

  for similarWord in similarWords:
    getWordScore(similarWord)

    #note: At this point it is possible to have a new word with score less than wordInfo.score, so lets check it at priorityQueue
    newWordInfo = wordsToProcess.queue[0]
    if(newWordInfo.score < wordInfo.score):
      wordsToProcess.get()
      generateAndGuessSimilarWords(newWordInfo)

    
def main():   
  getInputAndSetup()

  while True:
    wordInfo = wordsToProcess.get()
    generateAndGuessSimilarWords(wordInfo)

  time.sleep(1000)

main()
