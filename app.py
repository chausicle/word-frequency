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
        # warn user if there's no files in peer-reference-forms folder
        if len(os.listdir(os.path.join(desktop_path, 'peer-reference-forms'))) == 0:
            print('Please put in at least one form into "peer-reference-forms" for analysis')
            print(
                'Run code again once a folder named peer-reference-forms is located in Desktop with forms to analyze.')
            return None
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
                filename = file.split('.')[0]
                path_to_file = os.path.join(pwd, file)
                path_to_keywords = os.path.join(
                    desktop_path, 'word-frequency-output',
                    'keyword_dataframes', '{}_frequencies.csv'.format(filename)
                )

                # create DataFrame and save to output file keyword_dataframes
                keywords, df_keywords, success = keyword_dataframe(
                    path_to_file, filename, path_to_keywords, successful_analysis
                )
                # collect keywords for one large word frequency,
                # generate individual wordclouds
                # and save individual DataFrames
                if keywords != 'Error':
                    multiform_keywords.extend(keywords)
                    successful_analysis = success
                    path_to_wordcloud = os.path.join(
                        desktop_path, 'word-frequency-output',
                        'wordclouds', "{}_wordcloud.pdf".format(filename)
                    )

                    # create wordcloud and save to output file wordclouds
                    generate_wordcloud(keywords, path_to_wordcloud, filename)
                else:
                    print("Couldn't analyze file {}".format(file))

        end_time = datetime.datetime.now()
        analysis_time = end_time - start_time

        print('Analysis time start: {}'.format(start_time))
        print('Analysis time end: {}'.format(end_time))
        print('Successfully analyzed {} forms out of {}'.format(
            successful_analysis, file_length)
        )
        print('Runtime analysis: {} seconds'.format(analysis_time.seconds))
        print('\nBeginning to process multiform analysis...\n')

        start_time = datetime.datetime.now()
        path_to_multiform_frequency = os.path.join(
            desktop_path, 'word-frequency-output',
            'multiform_analysis', 'multiform_frequencies.csv'
        )
        path_to_multiform_wordcloud = os.path.join(
            desktop_path, 'word-frequency-output',
            'multiform_analysis', "multiform_wordcloud.pdf"
        )

        # create multiform frequency and save to output file multiform_analysis
        keyword_dataframe(
            '', 'multiform_frequencies',
            path_to_multiform_frequency, successful_analysis,
            True, multiform_keywords
        )

        # create multiform wordcloud and save to output file multiform_analysis
        generate_wordcloud(multiform_keywords, path_to_multiform_wordcloud)

        end_time = datetime.datetime.now()
        analysis_time = end_time - start_time

        print('Analysis time start: {}'.format(start_time))
        print('Analysis time end: {}'.format(end_time))
        print('Runtime analysis: {} seconds'.format(analysis_time.seconds))
    # prints out warning when peer-reference-forms folder isn't located in Desktop
    else:
        print('Missing folder name in Desktop: peer-reference-forms')
        print('Run code again once a folder named peer-reference-forms is located in Desktop with forms to analyze.')


def keyword_dataframe(
        path_to_file, filename,
        path_to_keywords, successful_analysis,
        is_multi=False, multiform_keywords=[],
        number_of_documents=1):
    """
    Generate word frequency DataFrame from text extracted off of document.

    :param path_to_file: Path to file
    :param filename: Name of file
    :param path_to_keywords: Path to keyword frequency folder
    :param successful_analysis: Number of successful analysis
    :param is_multi: Boolean to change process of analysis
    :param multiform_keywords: List of words from all successful analyzed documents
    :param number_of_documents: Integer for number of documents
    :return keywords: List of all keywords
    :return df_keywords: DataFrame of word frequencies
    :return successful_analysis: Counter for successful analyses
    """
    try:
        stopwords = set(STOPWORDS)
        # only extracts text from document if it's a single document
        if not is_multi:
            text = textract.process(path_to_file, method='tesseract',
                                language='eng', encoding='ascii'
                                ).decode('utf-8')

            # returns 3 Error strings just so code doesn't break
            # since the return is expected to unpack 3 variables
            if text == '':
                return 'Error', 'Error', 'Error'

            text = text.lower()
            keywords = re.findall(r'[a-zA-Z]\w+', text)
        else:
            number_of_documents = successful_analysis
            keywords = multiform_keywords

        df = pd.DataFrame(list(set(keywords)), columns=["keywords"])

        df['number_of_times_word_appeared'] = df['keywords']\
            .apply(lambda word: weightage(word, keywords, number_of_documents)[0])
        df['tf'] = df['keywords']\
            .apply(lambda word: weightage(word, keywords, number_of_documents)[1])
        df['idf'] = df['keywords']\
            .apply(lambda word: weightage(word, keywords, number_of_documents)[2])
        df['tf_idf'] = df['keywords']\
            .apply(lambda word: weightage(word, keywords, number_of_documents)[3])
        df['timestamp'] = datetime.datetime.now().isoformat()

        df = df.sort_values('tf_idf', ascending=True)
        df_keywords = df[~df['keywords'].isin(list(stopwords))]
        df_keywords.to_csv(path_to_keywords)
        successful_analysis += 1
        if not is_multi:
            print('DataFrame creation on file "{}" successful'.format(filename))
        else:
            print('DataFrame creation on all successful document analysis')

        return keywords, df_keywords, successful_analysis
    except Exception as e:
        print("""
        Error:
        
        {}
        """.format(e))
        return 'Error', 'Error', 'Error'


def weightage(word, text, number_of_documents=1):
    """
    Calculate number of times word appeared, term frequency,
    inverse document frequency, and product of term frequency and inverse document frequency

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


def generate_wordcloud(keywords, path_to_wordcloud, filename):
    """
    Generates wordcloud of text extracted from document

    :param keywords: String of keywords found from text
    :param path_to_wordcloud: String path to wordcloud folder
    :param filename: String of filename for printing on Terminal
    """
    word_cloud = WordCloud(width=800, height=800,
                           background_color='white',
                           stopwords=set(STOPWORDS),
                           min_font_size=10).generate(' '.join(keywords))

    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(word_cloud)
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(path_to_wordcloud)
    if not filename:
        print('Wordcloud creation on file "{}" successful'.format(filename))
    else:
        print('Worldcloud creation on all successful document analysis')

main()
