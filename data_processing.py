import os
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
#Reference: https://stackoverflow.com/questions/25534214/nltk-wordnet-lemmatizer-shouldnt-it-lemmatize-all-inflections-of-a-word
def is_noun(tag):
    return tag in ['NN', 'NNS', 'NNP', 'NNPS']


def is_verb(tag):
    return tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']


def is_adverb(tag):
    return tag in ['RB', 'RBR', 'RBS']


def is_adjective(tag):
    return tag in ['JJ', 'JJR', 'JJS']


def penn_to_wn(tag):
    if is_adjective(tag):
        return wn.ADJ
    elif is_noun(tag):
        return wn.NOUN
    elif is_adverb(tag):
        return wn.ADV
    elif is_verb(tag):
        return wn.VERB
    return None

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
                    if penn_to_wn(token[1]) == None:
                        token_str = token[0]+":Lemmatized:"+lemmatizer.lemmatize(token[0])+":POS:"+token[1]
                    else:
                        token_str = token[0]+":Lemmatized:"+lemmatizer.lemmatize(token[0],penn_to_wn(token[1]))+":POS:"+token[1]
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

o_file = open("data_processing_output.txt", "w")
for key, value in file_dict.items():
    if key is not "":
        o_file.write(str(key+": " + str(value)))
        o_file.write("\n")
o_file.close()
