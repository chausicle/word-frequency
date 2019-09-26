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
        # create a output folder if none is found on Desktop
        if 'word-frequency-output' not in os.listdir(desktop_path):
            os.makedirs(os.path.join(desktop_path, 'word-frequency-output'))
            os.makedirs(os.path.join(
                desktop_path, 'word-frequency-output', 'keyword_dataframes')
            )
            os.makedirs(os.path.join(
                desktop_path, 'word-frequency-output', 'wordclouds')
            )
            os.makedirs(os.path.join(
                desktop_path, 'word-frequency-output', 'multiform_analysis')
            )
        # checks if word-frequency-output folder has specified folders for output
        else:
            if 'keyword_dataframes' not in os.listdir(
                    os.path.join(desktop_path, 'word-frequency-output')):
                os.makedirs(os.path.join(
                    desktop_path, 'word-frequency-output', 'keyword_dataframes')
                )
            if 'wordclouds' not in os.listdir(
                    os.path.join(desktop_path, 'word-frequency-output')):
                os.makedirs(os.path.join(
                    desktop_path, 'word-frequency-output', 'wordclouds')
                )
            if 'multiform_analysis' not in os.listdir(
                    os.path.join(desktop_path, 'word-frequency-output')):
                os.makedirs(os.path.join(
                    desktop_path, 'word-frequency-output', 'multiform_analysis')
                )

        start_time = datetime.datetime.now()
        successful_analysis = 0
        multiform_keywords = []
        # walks each file to analyze
        for pwd, folders, files in os.walk(os.path.join(desktop_path, 'peer-reference-forms')):
            file_length = len(files)
            for file in files:
                path_to_file = os.path.join(pwd, file)
                filename = file.split('.')[0]

                keywords, df_keywords, unique, success = keyword_dataframe(
                    path_to_file, filename, successful_analysis
                )

                if keywords != 'Error':
                    multiform_keywords.extend(unique)
                    successful_analysis = success
                    df_keywords.to_csv(os.path.join(
                        desktop_path, 'word-frequency-output',
                        'keyword_dataframes', '{}_keywords.csv'.format(filename))
                    )
                else:
                    print("Couldn't analyze file {}".format(file))

        generate_wordcloud()

        end_time = datetime.datetime.now()
        analysis_time = end_time - start_time
        print('Analysis time start: {}'.format(start_time))
        print('Analysis time end: {}'.format(end_time))
        print('Successfully analyzed {} forms out of {}'.format(
            successful_analysis, file_length)
        )
        print('Runtime analysis: {}'.format(analysis_time.seconds))
    # prints out warning when peer-reference-forms folder isn't located in Desktop
    else:
        print('Missing folder name in Desktop: peer-reference-forms')
        print('Run code again once a folder named peer-reference-forms is located in Desktop with forms to analyze.')


def keyword_dataframe(path_to_file, filename, successful_analysis):
    """
    Generate word frequency DataFrames from text extracted off of forms.

    :param path_to_file: Path to file
    :param filename: Name of file
    :param successful_analysis: Number of successful analysis
    :return keywords: List of all keywords
    :return :
    :return:
    :return:
    """
    try:
        stopwords = set(STOPWORDS)

        text = textract.process(path_to_file, method='tesseract',
                                language='eng', encoding='ascii'
                                ).decode('utf-8')

        if text == '':
            return 'Error','Error','Error','Error'

        text = text.lower()
        keywords = re.findall(r'[a-zA-Z]\w+', text)

        df = pd.DataFrame(list(set(keywords)), columns=["keywords"])

        df['number_of_times_word_appeared'] = df['keywords'].apply(lambda word: weightage(word, keywords)[0])
        df['tf'] = df['keywords'].apply(lambda word: weightage(word, keywords)[1])
        df['idf'] = df['keywords'].apply(lambda word: weightage(word, keywords)[2])
        df['tf_idf'] = df['keywords'].apply(lambda word: weightage(word, keywords)[3])
        df['timestamp'] = datetime.datetime.now().isoformat()

        df = df.sort_values('tf_idf', ascending=True)
        df_keywords = df[~df['keywords'].isin(list(stopwords))]
        unique_keywords = list(filter(lambda word: word not in stopwords, keywords))
        successful_analysis += 1
        print('DataFrame creation on file "{}" successful'.format(filename))

        return ' '.join(keywords), df_keywords, unique_keywords, successful_analysis
    except Exception as e:
        print("""
        Error:
        
        {}
        """.format(e))
        return 'Error', 'Error', 'Error', 'Error'


def weightage(word, text, number_of_documents=1):
    """

    :param word: Word
    :param text: Keywords extracted into a list
    :param number_of_documents: Number of documents being analyzed. Default is 1
    :return number_of_times_word_appeared: Count of word in text
    :return tf: Term frequency
    :return idf: Inverse document frequency
    :return tf_idf: Product of term frequency and inverse document frequency
    """
    word_list = re.findall(word, ' '.join(text))
    number_of_times_word_appeared = len(word_list)
    tf = number_of_times_word_appeared / float(len(text))
    idf = np.log(number_of_documents / float(number_of_times_word_appeared))
    tf_idf = tf * idf

    return number_of_times_word_appeared, tf, idf, tf_idf


def generate_wordcloud():
    print('Generate wordcloud')


main()
