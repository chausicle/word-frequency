from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import platform
import datetime
import textract
import os
import re


def main():
    """
    Processes files from folder to generate a combined word frequency DataFrame and wordcloud
    and as well as individual DataFrames, of word frequency, and wordclouds.

    NOTE:
    Should place the files to be analyzed in a folder named 'peer-reference-forms'
    that's placed on the Desktop.

    Output:
    Puts individual word frequencies and wordclouds into a folder,
    'keyword_dataframes' and 'wordclouds' respectively, and also
    puts the multiform word frequency and wordcloud into a folder,
    'multiform_analysis'. All of these files will be placed in
    a folder named 'word-frequency-output'
    """
    which_plat = platform.system()

    # finds path to Desktop if on Windows OS
    if which_plat == 'Windows':
        desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    # finds path to Desktop if on Mac OS
    elif which_plat == 'Darwin':
        desktop_path = os.path.join(os.environ['HOME'], 'Desktop')

    # checks for peer-reference-forms folder in Desktop to analyze
    if 'peer-reference-forms' in os.listdir(desktop_path):
        start_time = datetime.datetime.now()
        # walks each file to analyze
        for pwd,folders,files in os.walk(desktop_path):

            for file in files:

                if which_plat == 'Windows':
                    path_to_file = pwd + '\\' + file
                elif which_plat == 'Darwin':
                    path_to_file = pwd + '/' + file

                filename = file.split('.')[0]
                keywords = keyword_dataframe(path_to_file, filename)

        end_time = datetime.datetime.now()
        analysis_time = end_time - start_time
        print('Analysis time start: {}'.format(start_time))
        print('Analysis time dnd: {}'.format(end_time))
        print('Runtime analysis: {}'.format(analysis_time.seconds))
        generate_wordcloud()
    # prints out warning when peer-reference-forms folder isn't located in Desktop
    else:
        print('Missing folder name in Desktop: peer-reference-forms')
        print('Run code again once a folder named peer-reference-forms is located in Desktop with forms to analyze.')


def keyword_dataframe(path_to_file, filename):
    """
    Generate word frequency DataFrames from text extracted off of forms.

    :param path_to_file: Path to file
    :param filename: Name of file
    :return:
    """
    weightage()

    return 'Change later'


def weightage():
    print('This is the weightage')


def generate_wordcloud():
    print('Generate wordcloud')

main()
