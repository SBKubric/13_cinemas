from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
import requests
import re
from bs4 import BeautifulSoup

SCHEDULE_URL = 'http://www.afisha.ru/msk/schedule_cinema/'
KINOPOISK_URL = 'https://plus.kinopoisk.ru/search/films/'
PROXY_LIST_URL = 'http://www.ip-adress.com/proxy_list/'
proxy = 'http://www.google.ie/gwt/x?u='


def get_random_proxy_url():
    ua = UserAgent()
    headers = {'referer': 'https://www.google.co.in/', 'User-Agent': ua.random, 'connection': 'close'}
    request = requests.get("http://www.ip-adress.com/proxy_list/", headers=headers)
    pattern = re.compile('.*<td>(.*)</td>.*<td>Elite</td>.*', re.DOTALL)
    matched = re.search(pattern, str(request.content))
    return matched.group(1)


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
    # proxy = get_random_proxy_url()
    ua = UserAgent()
    headers = {
        'referer': 'https://www.google.co.in/',
        'connection': 'close',
        'User-Agent': ua.random
    }
    params = {'text': movie_title}
    request = requests.get('{}{}'.format(proxy, KINOPOISK_URL), params=params, headers=headers, timeout=15)
    return request.content


def fetch_movie_url(search_page):
    if not search_page:
        return None
    search_page_soup = BeautifulSoup(search_page, 'html.parser')
    if search_page_soup.find(attrs={'class': 'search-empty'}):
        return None
    movie_url_tag = search_page_soup.find(attrs={'class': 'link film-snippet__media-content'})
    return movie_url_tag.get('href')


def fetch_movie_page(movie_url):
    if not movie_url:
        return None
    # proxy = get_random_proxy_url()
    ua = UserAgent()
    headers = {
        'connection': 'close',
        'User-Agent': ua.random
    }
    request = requests.get('{}{}'.format(proxy, movie_url), headers=headers, timeout=15)
    return request.content


def get_number_of_voices(movie_voices_counter_text):
    words = movie_voices_counter_text.split(' ')
    words = filter(lambda word: re.fullmatch('[0-9]*', word), words)
    number = int(''.join(words))
    return number


def fetch_movie_data_frm_page(movie_page):
    if not movie_page:
        return {
            'rating': 0,
            'voices_counter': 0
        }
    movie_page_soup = BeautifulSoup(movie_page, 'html.parser')
    movie_rating_text = movie_page_soup.find(attrs={'class': 'rating-button__rating'}).text
    movie_voices_counter_text = movie_page_soup.find(attrs={'class': 'film-header__rating-comment'}).text
    movie_data = {
        'rating': float(movie_rating_text) if movie_rating_text else 0,
        'voices_counter': get_number_of_voices(movie_voices_counter_text) if movie_rating_text else 0,
    }
    return movie_data


def fetch_movie_info(movie_title):
    # print('Fetching the {}'.format(movie_title))
    search_page = fetch_search_page(movie_title)
    movie_url = fetch_movie_url(search_page)
    movie_page = fetch_movie_page(movie_url)
    return fetch_movie_data_frm_page(movie_page)


def fetch_rating_and_voice_counter(afisha_data_list):
    movie_titles = list(
        afisha_data['title'] for afisha_data in afisha_data_list
    )
    pool = ThreadPoolExecutor(len(movie_titles))
    kinop_data_list = list(pool.map(fetch_movie_info, movie_titles))
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
    pass


if __name__ == '__main__':
    # print('Connecting to the {}...'.format(SCHEDULE_URL))
    # raw_html = fetch_afisha_page()
    # print('Scraping the movie name list...')
    # movie_data_list = parse_afisha_list(raw_html)[:5]
    # print('Scraping the rating and voice counters...')
    # fetch_rating_and_voice_counter(movie_data_list)
    # print('Analyzing the results...')
    # best_movies_list = select_the_best_movies(movie_data_list)
    # print('Printing the results...')
    # output_movies_to_console(movie_data_list)
    print(fetch_movie_info('Викинг'))