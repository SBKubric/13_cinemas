import requests
from bs4 import BeautifulSoup

SCHEDULE_URL = 'http://www.afisha.ru/msk/schedule_cinema/'


def fetch_afisha_page():
    afisha_page = requests.get(SCHEDULE_URL)
    return afisha_page.content


def parse_afisha_list(raw_html):
    afisha_soup = BeautifulSoup(raw_html, 'html.parser')
    title_tag_list = afisha_soup.find_all(attrs={'class': 'theme-item__title '})
    movie_titles_list = list(
        title_tag.findChild('a').text for title_tag in title_tag_list
    )
    schedule_tag = afisha_soup.find(attrs={'class': 'b-theme-schedule m-schedule-with-collapse'})  # type: BeautifulSoup
    cinemas_schedule_soups = schedule_tag.find_all('table')
    cinemas_counters = list(
        len(cinemas_schedule_soup.findChild('tbody')) for cinemas_schedule_soup in cinemas_schedule_soups
    )
    return ({
        'title': movie_title,
        'cinema_counter': cinemas_counter,
    } for movie_title, cinemas_counter in zip(movie_titles_list, cinemas_counters))


def fetch_movie_info(movie_title):
    pass


def output_movies_to_console(movies):
    pass


if __name__ == '__main__':
    raw_html = fetch_afisha_page()
    movie_data_list = parse_afisha_list(raw_html)
    for num, movie_data in enumerate(movie_data_list, start=1):
        print('{}. Title: {} Cinemas: {}'.format(num, movie_data['title'], movie_data['cinema_counter']))
