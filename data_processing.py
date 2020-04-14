import os
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn

lemmatizer = WordNetLemmatizer()
DIR = "WikipediaArticles"
file_dict = dict()
if __name__ == "__main__":
    for dirName, subdirList, fileList in os.walk(DIR):
        for file in fileList:
            contents = ""
            with open(DIR+"/"+file) as f:
                for line in f.readlines():
                    contents += line
            file_dict.update({file:contents})
    for file, text in file_dict.items():
        lines = text.split("\n")
        token_list = list()
        for line in lines:
            try:
                line = line.decode('utf-8')
                tokens = nltk.word_tokenize(line)
                tokens = nltk.pos_tag(tokens)
                lemma_list = list()
                for token in tokens:
                    #print(token[0])
                    token_str = token[0]+":Lemmatized:"+lemmatizer.lemmatize(token[0])+":POS:"+token[1]
                    synsets = wn.synsets(token[0])
                    for synset in synsets:
                        #print(str(synset)[8:-2])
                        synset = str(synset)[8:-2]
                        token_str += ":synset:"+str(synset)+":hyponyms:"+str(wn.synset(synset).hyponyms()) + ":hypernyms:"+str(wn.synset(synset).hypernyms()) + ":holonyms:"+str(wn.synset(synset).part_holonyms()) + ":meronyms:"+ str(wn.synset(synset).part_meronyms()) 
                    lemma_list.append(token_str)
                        

                token_list.append(lemma_list)
            except Exception as e:
                print(e)
        file_dict.update({file:token_list})
    print(file_dict)


