#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 14:54:31 2021

@author: jzimmer1
"""

from bs4 import BeautifulSoup
import os
import json
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import re
import string

import nltk
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download("stopwords")
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize 
from nltk.stem import 	WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords


# === === helper dict === === ===

contractions = { 
"ain't": "are not",
"aren't": "are not",
"can't": "cannot",
"can't've": "cannot have",
"'cause": "because",
"could've": "could have",
"couldn't": "could not",
"couldn't've": "could not have",
"didn't": "did not",
"doesn't": "does not",
"don't": "do not",
"hadn't": "had not",
"hadn't've": "had not have",
"hasn't": "has not",
"haven't": "have not",
"he'd": "he had",
"he'd've": "he would have",
"he'll": "he will",
"he'll've": "he will have",
"he's": "he is",
"how'd": "how did",
"how'd'y": "how do you",
"how'll": "how will",
"how's": "how is",
"I'd": "I had",
"I'd've": "I would have",
"I'll": "I will",
"I'll've": "I will have",
"I'm": "I am",
"I've": "I have",
"isn't": "is not",
"it'd": "it would",
"it'd've": "it would have",
"it'll": "it will",
"it'll've": "it will have",
"it's": "it is",
"let's": "let us",
"ma'am": "madam",
"mayn't": "may not",
"might've": "might have",
"mightn't": "might not",
"mightn't've": "might not have",
"must've": "must have",
"mustn't": "must not",
"mustn't've": "must not have",
"needn't": "need not",
"needn't've": "need not have",
"o'clock": "of the clock",
"oughtn't": "ought not",
"oughtn't've": "ought not have",
"shan't": "shall not",
"sha'n't": "shall not",
"shan't've": "shall not have",
"she'd": "she had",
"she'd've": "she would have",
"she'll": "she will",
"she'll've": "sshe will have",
"she's": "she is",
"should've": "should have",
"shouldn't": "should not",
"shouldn't've": "should not have",
"so've": "so have",
"so's": "so is",
"that'd": "that would",
"that'd've": "that would have",
"that's": "that is",
"there'd": "there had",
"there'd've": "there would have",
"there's": "there is",
"they'd": "they had",
"they'd've": "they would have",
"they'll": "they will",
"they'll've": "they will have",
"they're": "they are",
"they've": "they have",
"to've": "to have",
"wasn't": "was not",
"we'd": "we had",
"we'd've": "we would have",
"we'll": "we will",
"we'll've": "we will have",
"we're": "we are",
"we've": "we have",
"weren't": "were not",
"what'll": "what will",
"what'll've": "what will have",
"what're": "what are",
"what's": "what is",
"what've": "what have",
"when's": "when is",
"when've": "when have",
"where'd": "where did",
"where's": "where is",
"where've": "where have",
"who'll": "who will",
"who'll've": "who will have",
"who's": "who is",
"who've": "who have",
"why's": "why is",
"why've": "why have",
"will've": "will have",
"won't": "will not",
"won't've": "will not have",
"would've": "would have",
"wouldn't": "would not",
"wouldn't've": "would not have",
"y'all": "you all",
"y'all'd": "you all would",
"y'all'd've": "you all would have",
"y'all're": "you all are",
"y'all've": "you all have",
"you'd": "you had",
"you'd've": "you would have",
"you'll": "you will",
"you'll've": "you will have",
"you're": "you are",
"you've": "you have"
}

# === === Helper functions === ===
def write_json(data, filename):
    with open(filename,"w") as f:
        json.dump(data,f)
    return None
def get_json(filename):
    with open(filename) as f:
        jsonobj = json.load(f)
    return jsonobj
    
# === === === === === === === === 

class CamelotConfTranscript():
    def __init__(self, DirName):
        self.DirName = DirName
        self.text = self.get_transcript_text()
        self.clean = self.clean_text()
        self.exp1 = self.expand_cont()
        self.exp = self.exp1.lower()
        self.punc_dict = get_json("PCC_nostem_somepunctuation.json")
        self.worddict = self.wordlist()
        self.comb = self.combine()
        self.show_it()
    def get_transcript_text(self):
        allfiles = os.listdir(self.DirName)
        alltext = ""
        for f in allfiles:
            soup = BeautifulSoup(open(self.DirName+f,encoding="ISO-8859-1"),features="lxml")
            allps = soup.find_all('p',class_="style7")
            for p in allps:
                alltext += p.get_text()
        return alltext
    def clean_text(self):
        #remove everything between [...]
        asidespattern = r'\[.*\]'
        asidesmatches = re.findall(asidespattern, self.text)
        new_text = re.sub(asidespattern,'',self.text)
        #remove the transcription team note between **...**
        notepattern = r'\*\*.*\*\*'
        notematches = re.findall(notepattern, new_text)
        text = re.sub(notepattern,'',new_text)
        #remove the text "Click here for the video interview"
        text1 = re.sub(r'Click here for the video interview','',text)
        #remove people's inititals (indicating speaker)
        text2 = re.sub(r'DO[\'|’]F[\W]*[[0-9][0-9]]*:|DO[\'|’]F:','',text1)
        text3 = re.sub(r'[A-Z][A-Z][\W]*[[0-9][0-9]]*:|[A-Z][A-Z]:','',text2)
        #matches = re.findall(r'[A-Z][A-Z][\W]*[[0-9][0-9]]*:|[A-Z][A-Z]:',text2)
        #print(matches)
        #print(text3)
        #remove punctuation except for - (as in mind-controlled) (and some other random stuff)
        text4 = re.sub(r'\W*[,|.|!|?|…|\:|\;|”|\'|“|...|/|’|\(|\)]\W+',' ',text3)
        #remove all the punctuation (which will mess up e.g. "x-files")
        #text4 = re.sub(r'\W*[\.|\!|\?|…|...|/|’|\(|\)|\#|\$|%|\&|-|--|,|\'|\'\']\W+',' ',text3)
        #text4 = text3.translate(str.maketrans(' ', ' ', string.punctuation)) #this actually kinda sucks
        text5 = re.sub(r'…','',text4)
        text6 = re.sub(r'--','',text5)
        return text6
    def expand_cont(self):
        text = self.clean
        for cont in contractions:
            if "/" in contractions[cont]:
                pass
            else:
                parts = cont.split("'")
                new = ""
                for i in range(1,len(parts)):
                    new += parts[i-1]+"['|’]"
                new  +=  parts[-1]   
                recont = re.compile(new, re.IGNORECASE)
                expre = contractions[cont]
                matches = re.findall(recont, text)
                text = re.sub(recont,expre,text)
        #write_json(text, "guess_ambiguous_contractions.json")
        return text
    def wordlist(self):
        text = self.exp
        lemmas = []
        #wordnet_lemmatizer = WordNetLemmatizer()
        tokenization = nltk.word_tokenize(text)
        
        #stemmer = SnowballStemmer("english")
        #print(tokenization)
        #for w in tokenization:
            #pass
            #lemmas += [wordnet_lemmatizer.lemmatize(w)]
            #lemmas += [stemmer.stem(w)]
            
        #print(lemmas)
        lemmas=tokenization
        lemmadict = {x:0 for x in tokenization}
        for w in lemmas:
            if w in lemmadict:
                lemmadict[w] += 1
            else:
                pass
        #print(sorted(lemmadict))
        #write_json(lemmadict, "snowball_stem_PCC_freq.json")
        #write_json(lemmadict, "PCC_nostem_somepunctuation.json")
        
        return lemmadict
    def combine(self):
        dicti = self.worddict
        keys = [x for x in self.worddict]
        for w in keys:
            if w[-1] == "s":
                if w[:-1] in dicti:
                    #print(w, w[:-1])
                    dicti[w[:-1]]+=dicti[w]
                    del dicti[w]
            if w[-1] == "y" and len(w) >= 6:
                if w[:-2] in dicti:
                    #print(w, w[:-2])
                    dicti[w[:-2]]+=dicti[w]
                    del dicti[w]
            if (w[-1] == "d" or w[-1] == "r") and len(w) >= 6:
                if w[:-2] in dicti and w not in ("former"):
                    if w[-2] == "e":
                        #print(w, w[:-2])
                        dicti[w[:-2]]+=dicti[w]
                        del dicti[w]
        #write_json(dicti,"combining_end_in_ed_er_words.json")
        #print(dicti)
        return dicti
    def show_it(self):
        dicti = self.comb
        sorteddict = {k: v for k, v in sorted(dicti.items(), key=lambda item: item[1])}
        #print(sorteddict)
        nostops = {k: v for k, v in sorted(dicti.items(), key=lambda item: item[1]) if k not in stopwords.words('english')}
        #print(nostops)
        punctuation = ['’','–',']','&',"''",'``','“','-','(','[','$']
        #print("before: ",len(nostops))
        for p in punctuation:
            if p in nostops:
                #print(p)
                del nostops[p]
            else:
                print("missing: ",p)
        #print("after: ",len(nostops), len(punctuation), len(nostops)+len(punctuation))
        #write_json(nostops, "nostopwords_minuspunctuation.json")
        count = 0
        df = pd.DataFrame()
        labels = []
        vals = []
        totalwords = sum([nostops[i] for i in nostops])
        print(len(nostops))
        for key, value in sorted(nostops.items(), key=lambda kv: kv[1], reverse=True):
            #print(key, value/totalwords)
            if 0 <= count < 657:
                df[key]=[value]
                labels += [key]
                vals += [df[key]]
            if count > 600:
                break
            count += 1
        #print(df.head())
        #g = sns.barplot(data=df,orient="h")
        #print(labels)
        write_json(labels,"top_10percent_nostops.json")
        #g.set_xticklabels(labels=labels,rotation=90)
    

    

    

CamelotConfTranscript("ProjectCamelotConference/")


