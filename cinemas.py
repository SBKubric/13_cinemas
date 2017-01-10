import random
import requests
import sys
from bs4 import BeautifulSoup

IS_ARTHOUSE_PARAMETER = 15
PROXY_API_URL = 'http://www.freeproxy-list.ru/api/proxy'
SCHEDULE_URL = 'http://www.afisha.ru/msk/schedule_cinema/'
KINOPOISK_URL = 'https://www.kinopoisk.ru/index.php'
TIMEOUT = 10
TOP = 10
BAR_LENGTH = 40


def update_progress(progress):
    bar_length = BAR_LENGTH
    status = ''
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        raise TypeError('progress value must be float!')
    if progress < 0:
        progress = 0
        status = 'Halt...\r\n'
    if progress >= 1:
        progress = 1
        status = 'Done!\r\n'
    block = int(round(bar_length * progress))
    text = '\rLoading: [{}] {:.2f}% {}'.format('#' * block + '-' * (bar_length - block), progress * 100, status)
    sys.stdout.write(text)
    sys.stdout.flush()


def fetch_afisha_page():
    afisha_page = requests.get(SCHEDULE_URL)
    return afisha_page.content


def get_mainstream_list(movie_titles_list, cinemas_counters):
    no_arthouse = []
    for movie_title, counter in zip(movie_titles_list, cinemas_counters):
        if IS_ARTHOUSE_PARAMETER < counter:
            no_arthouse.append(
                {
                    'title': movie_title,
                    'theaters': counter,
                }
            )
    return no_arthouse


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
    mainstream_list = get_mainstream_list(movie_titles_list, cinemas_counters)
    return mainstream_list


def get_random_user_agent():
    u_agents = [
        'Mozilla/5.0 (X11; Linux i686; rv:50.0) Gecko/20100101 Firefox/50.0',
        'Opera/9.80 (Windows NT 6.2; WOW64) Presto/2.12.388 Version/12.17',
        'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0) Gecko/20100101',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        """Mozilla/5.0 (Windows NT 10.0; Win64; x64)
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246""",

    ]
    return random.choice(u_agents)


def fetch_proxy_list():
    params = {'anonymity': 'false',
              'token': 'demo'}
    response = requests.get(PROXY_API_URL, params=params).text
    proxies = response.split('\n')
    return proxies


def load_kinop_page(movie_title, proxy_list):
    try:
        params = {'kp_query': movie_title,
                  'first': 'yes'}
        headers = {'Accept': 'text/plain',
                   'Accept-Encoding': 'UTF-8',
                   'Accept-Language': 'Ru-ru',
                   'Content-Type': 'text/html;charset=UTF-8',
                   'User-Agent': 'Agent:{}'.format(get_random_user_agent()), }
        proxy = {"http": random.choice(proxy_list)}
        response = requests.session().get('http://kinopoisk.ru/index.php',
                                          params=params,
                                          headers=headers,
                                          proxies=proxy,
                                          timeout=TIMEOUT)
    except (requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ProxyError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.InvalidHeader,
            ) as network_error:
        return None
    else:
        if response.status_code == (502 or 403):
            return None
        else:
            return response.content


def get_kinop_page(movie_title):
    proxy_list = fetch_proxy_list()
    response = None
    while not response:
        response = load_kinop_page(movie_title, proxy_list)
        if response:
            return response


def parse_kinop_page(search_page):
    search_page_soup = BeautifulSoup(search_page, 'html.parser')
    average_rating_tag = search_page_soup.find('meta', attrs={'itemprop': 'ratingValue'})
    voters_counter_tag = search_page_soup.find('span', attrs={'class': 'ratingCount'})
    return {
        'rating': get_rating(average_rating_tag.get('content')) if average_rating_tag is not None else 0,
        'voters': get_voters_counter(voters_counter_tag.text) if voters_counter_tag is not None else 0,
    }


def get_rating(string_rating):
    try:
        return float(string_rating)
    except ValueError:
        return 0


def get_voters_counter(movie_voters_counter):
    digits = list(s for s in movie_voters_counter.split() if s.isdigit())
    try:
        return int(''.join(digits))
    except ValueError:
        return 0


def fetch_movie_rating(movie_title):
    kinop_html_raw = get_kinop_page(movie_title)
    movie_rating_and_voters_counter = parse_kinop_page(kinop_html_raw)
    return movie_rating_and_voters_counter


def add_rating_and_voters_counter(afisha_data_list):
    movie_titles = list(
        afisha_data['title'] for afisha_data in afisha_data_list
    )
    kinop_data_list = []
    progress = 0
    update_progress(progress)
    for movie_title in movie_titles:
        kinop_data = fetch_movie_rating(movie_title)
        progress += 1
        update_progress(progress/len(movie_titles))
        kinop_data_list.append(kinop_data)

    for afisha_data, kinop_data in zip(afisha_data_list, kinop_data_list):
        for key, value in zip(kinop_data.keys(), kinop_data.values()):
            afisha_data[key] = value


def output_movies_to_console(movie_data_list):
    for num, movie_data in enumerate(movie_data_list, start=1):
        print('{}. Title: {}\n   Rating: {} Total amount of voters: {} Number of cinemas: {}'.format(
            num, movie_data['title'], movie_data['rating'], movie_data['voters'], movie_data['theaters']
        ))
        print()


def select_the_best_movies(movie_data_list):
    return sorted(movie_data_list, key=lambda movie_data: movie_data['rating'], reverse=True)[:TOP]


if __name__ == '__main__':
    print('Connecting to the {}...'.format(SCHEDULE_URL))
    raw_html = fetch_afisha_page()
    print('Scraping the movie name list...')
    movie_data_list = parse_afisha_list(raw_html)
    print('Scraping the rating and voice counters...')
    add_rating_and_voters_counter(movie_data_list)
    print('Analyzing the results...')
    best_movies_list = select_the_best_movies(movie_data_list)
    print('Printing the results...')
    output_movies_to_console(best_movies_list)