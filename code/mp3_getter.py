import time
import shutil
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


# from the accent.gmu website, pass in list of languages to scrape mp3 files and save them to disk
def mp3getter(lst):  # Gets all the mp3 of the given languages
    url = "http://accent.gmu.edu/soundtracks/"
    for j in range(len(lst)):
        for i in range(1, lst[j][1]+1):
            while True:
                try:
                    fname = f"{lst[j][0]}{i}"
                    mp3 = requests.get(url+fname+".mp3")
                    print(f"\nDownloading {fname}.mp3")
                    with open(f"Audio/{fname}.mp3", "wb") as audio:
                        audio.write(mp3.content)
                except:
                    # Once file finishes downloading, a buffer time to make sure next download doesn't start too early
                    time.sleep(2)
                else:
                    break  # To break the while loop


def get_languages():  # General function to return all languages, basically useless for us coz we choose our languages
    url = "http://accent.gmu.edu/browse_language.php"
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    languages = []
    language_lists = soup.findAll('ul', 'languagelist')
    for ul in language_lists:
        for li in ul.findAll('li'):
            languages.append(li.string)
    return languages


def get_language_urls(lst):  # Just returns list of urls of each language, not much use
    urls = []
    for language in lst:
        urls.append(
            'http://accent.gmu.edu/browse_language.php?function=find&language=' + language)
    return urls


# from language, get the number of speakers of that language
def get_num(language):  # Returns the num of samples for a given language, useful in below function
    url = 'http://accent.gmu.edu/browse_language.php?function=find&language=' + language
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    div = soup.find_all('div', 'content')
    try:
        num = int(div[0].h5.string.split()[2])
    except AttributeError:
        num = 0
    return num


# from list of languages, return list of tuples (LANGUAGE, LANGUAGE_NUM_SPEAKERS) for mp3getter, ignoring languages
# with 0 speakers
# Returns a list of tuples, (lang, num), mainly used for the mp3getter function
def get_formatted_languages(languages):
    formatted_languages = []
    for language in languages:
        num = get_num(language)
        if num != 0:
            formatted_languages.append((language, num))
    return formatted_languages


def get_speaker_info(start, stop):
    '''
    Inputs: two integers, corresponding to min and max speaker id number per language
    Outputs: Pandas Dataframe containing speaker filename, birthplace, native_language, age, sex, age_onset of English
    '''

    user_data = []
    for num in range(start, stop):
        info = {'speakerid': num, 'filename': 0, 'birthplace': 1,
                'native_language': 2, 'age': 3, 'sex': 4, 'age_onset': 5}
        url = "http://accent.gmu.edu/browse_language.php?function=detail&speakerid={}".format(
            num)
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'html.parser')
        body = soup.find_all('div', attrs={'class': 'content'})
        try:
            info['filename'] = str(body[0].find('h5').text.split()[0])
            bio_bar = soup.find_all('ul', attrs={'class': 'bio'})
            info['birthplace'] = str(bio_bar[0].find_all('li')[0].text)[13:-6]
            info['native_language'] = str(
                bio_bar[0].find_all('li')[1].text.split()[2])
            info['age'] = float(bio_bar[0].find_all(
                'li')[3].text.split()[2].strip(','))
            info['sex'] = str(bio_bar[0].find_all(
                'li')[3].text.split()[3].strip())
            info['age_onset'] = float(bio_bar[0].find_all('li')[
                                      4].text.split()[4].strip())
            user_data.append(info)
        except:
            info['filename'] = ''
            info['birthplace'] = ''
            info['native_language'] = ''
            info['age'] = ''
            info['sex'] = ''
            info['age_onset'] = ''
            user_data.append(info)
        df = pd.DataFrame(user_data)
        df.to_csv('speaker_info_{}.csv'.format(stop))
    return df


if __name__ == "__main__":
    # Add the function call here
    langs = ['arabic', 'english', 'french', 'german', 'hindi',
             'kannada', 'mandarin', 'russian', 'spanish', 'yao']
    lang_tuple = get_formatted_languages(langs)
    print(lang_tuple)
    # [('arabic', 194), ('english', 646), ('french', 80), ('german', 42), ('hindi', 34), ('kannada', 9), ('mandarin', 150), ('russian', 81), ('spanish', 228)]
    print('Downloading now...')
    mp3getter(lang_tuple)
    print("DONE!!")
