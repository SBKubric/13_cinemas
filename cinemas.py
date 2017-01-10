import requests
import sys
import time
from bs4 import BeautifulSoup

SCHEDULE_URL = 'http://www.afisha.ru/msk/schedule_cinema/'
KINOPOISK_URL = 'https://www.kinopoisk.ru/index.php'
TIMEOUT = 13
TOP = 20


def update_progress(progress):
    bar_length = 10 # Modify this to change the length of the progress bar
    status = ''
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = 'error: progress var must be float\r\n'
    if progress < 0:
        progress = 0
        status = 'Halt...\r\n'
    if progress >= 1:
        progress = 1
        status = 'Done...\r\n'
    block = int(round(bar_length*progress))
    text = '\rPercent: [{}] {}% {}'.format('#'*block + '#'*(bar_length-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()


def calculate_progress():
    pass


def fetch_afisha_page():
    afisha_page = requests.get(SCHEDULE_URL)
    return afisha_page.content


def parse_afisha_list(raw_html):
    afisha_soup = BeautifulSoup(raw_html, 'html.parser')
    title_tag_list = afisha_soup.find_all(attrs={'class': 'm-disp-table'})
    movie_titles_list = list(
        title_tag.findChild('a').text for title_tag in title_tag_list
    )
    schedule_tag = afisha_soup.find(attrs={'class': 'b-theme-schedule m-schedule-with-collapse'})  # type: BeautifulSoup
    cinemas_schedule_soups = schedule_tag.find_all('table')
    cinemas_counters = list(
        len(cinemas_schedule_soup.findChild('tbody')) for cinemas_schedule_soup in cinemas_schedule_soups
    )
    return list({
        'title': movie_title,
        'cinema_counter': cinemas_counter,
    } for movie_title, cinemas_counter in zip(movie_titles_list, cinemas_counters))


def fetch_search_page(movie_title):
    params = {
        'first': 'yes',
        'what': None,
        'kp_query': movie_title,
    }
    request = requests.get(KINOPOISK_URL, params=params, timeout=15)
    return request.content


def fetch_movie_data(search_page):
    if not search_page:
        return {
            'rating': 0,
            'voices_counter': 0
        }
    search_page_soup = BeautifulSoup(search_page, 'html.parser')
    if search_page_soup.find(attrs={'class': 'search-empty'}):
        return {
            'rating': 0,
            'voices_counter': 0
        }
    movie_average_rating = search_page_soup.find('span', class_='rating_ball').text
    voters_counter = search_page_soup.find('span', class_='ratingCount').text
    print(movie_average_rating, voters_counter)
    return {
        'rating': float(movie_average_rating),
        'voters': int(get_voters_counter(voters_counter)),
    }


def get_voters_counter(movie_voters_counter_text):
    digits = list(s for s in movie_voters_counter_text.split() if s.isdigit())
    return int(''.join(digits))


def fetch_movie_info(movie_title):
    search_page = fetch_search_page(movie_title)
    movie_data = fetch_movie_data(search_page)
    return movie_data


def fetch_rating_and_voters_counter(afisha_data_list):
    movie_titles = list(
        afisha_data['title'] for afisha_data in afisha_data_list
    )
    kinop_data_list = []
    progress = 0
    update_progress(float(progress))
    for movie_title in movie_titles:
        kinop_data_list.append(fetch_movie_info(movie_title))
        time.sleep(TIMEOUT)
        progress += 1
        update_progress(progress/len(movie_titles))
    for afisha_data, kinop_data in zip(afisha_data_list, kinop_data_list):
        for key, value in zip(kinop_data.keys(), kinop_data.values()):
            afisha_data[key] = value


def output_movies_to_console(movie_data_list):
    for num, movie_data in enumerate(movie_data_list, start=1):
        print('{}. Title: {}\n   Rating: {} Total amount of voters: {} Number of cinemas: {}'.format(
            num, movie_data['title'], movie_data['rating'], movie_data['voices_counter'], movie_data['cinema_counter']
        ))
        print()


def select_the_best_movies(movie_data_list):
    return sorted(movie_data_list, key=movie_data_list['rating'])[:TOP]


if __name__ == '__main__':
    # print('Connecting to the {}...'.format(SCHEDULE_URL))
    # raw_html = fetch_afisha_page()
    # print('Scraping the movie name list...')
    # movie_data_list = parse_afisha_list(raw_html)[:5]
    # print('Scraping the rating and voice counters...')
    # fetch_rating_and_voters_counter(movie_data_list)
    # print('Analyzing the results...')
    # best_movies_list = select_the_best_movies(movie_data_list)
    # print('Printing the results...')
    # output_movies_to_console(best_movies_list)
    fetch_movie_info('Викинг 18+')