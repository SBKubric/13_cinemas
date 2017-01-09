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
    return movie_titles_list


def fetch_movie_info(movie_title):
    pass


def output_movies_to_console(movies):
    pass


if __name__ == '__main__':
    raw_html = fetch_afisha_page()
    movie_titles_list = parse_afisha_list(raw_html)
    for num, movie_title in enumerate(movie_titles_list, start=1):
        print('{}. {}'.format(num, movie_title))
