# ContextoBot
AI to play the game https://contexto.me/

A crawler using selenium library (https://selenium-python.readthedocs.io/) and spaCy library (https://spacy.io/) to find words in a same context and find the key term to finish the game

#1 Library dependencies:
You need to install the following libraries: Selenium, spaCy, Numpy, and maybe another one that you do not have

#2 Downloads: You need to download the chrome driver (https://chromedriver.chromium.org/downloads) and put it in the path of "DRIVER_PATH" (you may change it if you want)

It is needed to download the "pt_core_news_lg" model, the site https://spacy.io/models/pt shows how to download it

#3 Run it and enjoy :)


#ToDo:
1- Find similar words from a vector of words
2- Remove every similar word with the same radical, that leads to try the "same word" again and again (need to test)
3- filter words with stranges symbols (@%$#!)
4- Remove plural, check it
5- Set verb tense to infitive, check it
