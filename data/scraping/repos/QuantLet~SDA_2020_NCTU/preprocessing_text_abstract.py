# -*- coding: utf-8 -*-
"""preprocessing_text.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qhcgAMgMTDwpnISj5W3NyTeHN5mSZgV_
"""

# Install Library
import pandas as pd
import numpy as np
import io
import nltk
import gensim
from gensim import corpora
nltk.download ('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer
from nltk.stem import WordNetLemmatizer 
from nltk import pos_tag
from pandas import DataFrame
#from gensim.models import HdpModel
#from gensim.models.coherencemodel import CoherenceModel
import string
import re

# Import data
data = pd.read_csv('data_abstract.csv', sep=';')
data_abstract = data.abstract
data_title = data.title

# Import stopwords
additional_word = ['covid-19', '2019-ncov', 'sars-ncov-2', 'sars-cov-2', 'sarscov','covid19', 'cov', 'sarcov2', 'sarscov2', 'coronavirus','coronavirus2','use',
                   'cooky', 'help', 'provide', 'enhance', 'service', 'tailor', 'content', 'agree', 'copyright', 'cookies',
                   'elsevier', 'bv', 'licensors', 'sciencedirect', 'trademark', 'elsevier', 'bv', 'ad', 'continue', 'contributor', 'register']
stop_words = stopwords.words('english')

# Preprocess function
def preprocess_text(text, stopwords, additional_word):
  # Case folding
  abstract_lower = []
  for line in text:
    result = line.lower()
    abstract_lower.append(result)
  # Lemmatizer, Stemming, Tokenizing
  lemmatizer = WordNetLemmatizer() 
  datas = []
  dtl = []
  data_clean = []
  b4lemma = []
  for d in abstract_lower:
    wo = re.sub(r'[^\w\s]', '', d) 
    wo = word_tokenize(wo)
    a = []
    b4lemma = d
    for w in wo:
      if(w in stop_words or w[0].isdigit()):
        None
      else:
        a.append(w)
    datal = []
    for word, tag in pos_tag(a):
      wntag = tag[0].lower()
      wntag = wntag if wntag in ['a', 'r', 'n', 'v'] else None
      lemma = lemmatizer.lemmatize(word, wntag) if wntag else word
      if (not lemma in additional_word):
        datal.append(lemma) 
    wo = ' '.join(map(str, datal))
    dtl.append(datal)
    if wo !='':
      data_clean.append(wo)
  return data_clean

# Run preprocess
abstract_clean = preprocess_text(data_abstract, stop_words, additional_word)
abstract_clean = pd.DataFrame(abstract_clean, columns= ['abstract'])
abstract_clean.to_csv('abstract_clean.csv', index=False, index_label=False)