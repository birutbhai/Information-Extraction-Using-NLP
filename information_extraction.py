import os
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import spacy
import neuralcoref
import en_core_web_sm

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
nlp = spacy.load('en')
neuralcoref.add_to_pipe(nlp)

DIR = "test"
file_dict = dict()
coref_dict = dict()

if __name__ == "__main__":
    for dirName, subdirList, fileList in os.walk(DIR):
        for file in fileList:
            contents = ""
            with open(DIR+"/"+file) as f:
                try:
                    for line in f.readlines():
                        contents += line
                except Exception as e1:
                    print("Excaption", e1)
            file_dict.update({file:contents})
    for file, text in file_dict.items():
        try:
            ref_text = ""
            paras = text.split("\n")
            #text = text.decode('utf-8')
            for para in paras:
                try:
                #print (para)
                    doc = nlp(para)
                    for token in doc:
                        if token._.in_coref:
                            tok = ""
                            #print (token._.coref_clusters)
                            for cluster in token._.coref_clusters:
                                #print (token.text + " => " + cluster.main.text)
                                tok = cluster.main.text
                            ref_text = ref_text + " " + str(tok)
                        else:
                            ref_text = ref_text + " " + str(token)
                except Exception as e1:
                    print("Excaption", e1)
            coref_dict.update({file:ref_text})
        except Exception as e:
            print("Excaption", e)
    #print(coref_dict)

    nlp = spacy.load('en_core_web_sm')
    from spacy.matcher import Matcher
    from spacy.tokens import Span
    import json
    #Place formats
    pattern1 = [{'POS':'PROPN'},
                {"OP": "*"},
                {'LOWER': 'in'},
                {'POS': 'PROPN'}]
    pattern2 = [{'POS':'PROPN'},
                {"OP": "*"},
                {'LOWER': 'part'},
                {'LOWER': 'of'},
                {'POS': 'PROPN'}]
    pattern3 = [{'POS':'PROPN'},
                {'LOWER': ','},
                {'POS': 'PROPN'}]
    pattern4 = [{'POS':'PROPN'},
                {'POS':'NOUN'},
                {'LOWER': 'of'},
                {'POS': 'PROPN'}]
    pattern5 = [{'POS':'PROPN'},
                {"OP": "*"},
                {'LOWER': 'in'},
                {'POS': 'PROPN'},
                {'LOWER': 'and'},
                {'POS': 'PROPN'}]

    matcher = Matcher(nlp.vocab)
    matcher.add(1, None, pattern1)
    matcher.add(2, None, pattern2)
    matcher.add(3, None, pattern3)
    matcher.add(4, None, pattern4)
    matcher.add(5, None, pattern5)
    json_list = list()
    for file, text in file_dict.items():
        try:
            file_extraction_list = list()
            sentences = nltk.sent_tokenize(text)
            for sentence in sentences:
                try:
                    doc = nlp(sentence)
                    print("Sentence: "+sentence)
                    #for token in doc:
                        #print(token.text,token.pos_)
                    place_count = 0
                    for X in doc.ents:
                        if str(X.label_) == "GPE" or str(X.label_) == "NORP'":
                            place_count = place_count + 1
                    if place_count >=  1:
                        matches = matcher(doc)
                        for match in matches:
                            match_patter_id = match[0]
                            span = doc[match[1]:match[2]]
                            tokens = str(span.text).split()
                            #print(span.text)
                            places = [tokens[0],tokens[len(tokens)-1]]
                            match_count = 0
                            for X in doc.ents:
                                if X.text == places[0] and X.label_ == "GPE" or str(X.label_) == "NORP":
                                    match_count = match_count + 1
                                if X.text == places[1] and X.label_ == "GPE" or str(X.label_) == "NORP":
                                    match_count = match_count + 1
                            if match_count >=  1:
                                first_place = places[0]
                                second_place = places[1]
                                if match_patter_id == 4:
                                    first_place = places[1]
                                    second_place = places[0]
                                print("Location:"+first_place+"-->"+second_place)
                                file_extraction_list.insert(len(file_extraction_list), {"template": "PART", "sentences": sentence, "arguments": {"1": first_place, "2":second_place}})
                                #print("extraction: ", file_extraction_list)
                        print([(X.text, X.label_) for X in doc.ents])
                except Exception as e1:
                    print("Exception:", e1)
            json_list.insert(len(json_list), {"document": file, "extraction":file_extraction_list})
        except Exception as e:
            print("Exception:", e)

    json_file =json.dumps(json_list)
    o_file = open("output.json", "w")
    o_file.write(json_file)
    o_file.close()

    
