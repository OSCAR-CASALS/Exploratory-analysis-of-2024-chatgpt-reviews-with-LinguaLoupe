'''
Clean data from sample datasets
'''

import os
import pandas as pd
from lingua import LanguageDetectorBuilder, Language
#from langdetect import detect
#from transformers import pipeline
from ftlangdetect import detect

# Load dataset
df = pd.read_csv('CHATGPT.csv')

# Remove empty reviews

clean_df = df[df['Review'].isnull() == False]

empty_df = df[df['Review'].isnull() == True]


# Load lingua

detector = LanguageDetectorBuilder.from_all_spoken_languages().build()


def meta_is_text_en(text):
    '''
    Use fasttext-langdetect to see if a text is in english.
    '''
    
    result = detect(text = text, low_memory=False)

    label = result['lang']
    if label == "en":
        return True
    
    return False


def lingua_is_text_english(text):
    '''
    Use lingua-language-detector to see if a text is in english
    '''
    try:
        res = detector.detect_language_of(text)
    except:
        print("Could not classify the following text with lingua:", text)
        return False

    if res == Language.ENGLISH:
        return True

    return False


# Use fasttext-langdetect to detect english reviews.

en_reviews = clean_df['Review'].apply(meta_is_text_en).tolist()

no_en = [not elem for elem in en_reviews]

clean_df_en = clean_df[en_reviews]

non_en_reviews = clean_df[no_en]

# Second screening of english reviews with lingua-language-detector.

revised_no_en = non_en_reviews['Review'].apply(lingua_is_text_english).tolist()

# Save discarded reviews in it's own dataset and export everything to csv

revised_reviews_still_no_en = [not elem for elem in revised_no_en]

revised_reviews = non_en_reviews[revised_no_en]

non_en_reviews = non_en_reviews[revised_reviews_still_no_en]

empty_df_concat = pd.concat([
    empty_df,
    non_en_reviews
    ], ignore_index=True)

empty_df_concat.to_csv('Discarded_Reviews.csv', index = False)

empty_df_concat.groupby('label').size().to_csv('Ammount_of_Discarded_Reviews.csv')

clean_df_en.to_csv('CHATGPT_Reviews_Clean.csv', index = False)

revised_reviews.to_csv('Revised_Reviews.csv', index=False)