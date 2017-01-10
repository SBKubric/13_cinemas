# Cinemas

## Description

The script shows 10 the most popular movies that are currently in theatres.

## Installation

The script is written with Python3.

Install the packages from requirements.txt using pip:

```
pip install -r requirements.txt
```

**IMPORTANT**: best practice is to use virtualenv. See here: [Link](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

## Example

**INPUT:**
```
python3 cinemas.py
```

**OUTPUT:**

```
Connecting to the http://www.afisha.ru/msk/schedule_cinema/...
Scraping the movie name list...
Scraping the rating and voice counters...
Loading: [########################################] 100.00% Done!
Analyzing the results...
Printing the results...
1. Title: Моана
   Rating: 7.8 Total amount of voters: 12774 Number of cinemas: 53

2. Title: Изгой-один: Звездные войны. Истории
   Rating: 7.5 Total amount of voters: 39899 Number of cinemas: 110

3. Title: Призрачная красота
   Rating: 7.2 Total amount of voters: 11369 Number of cinemas: 18

4. Title: Пассажиры
   Rating: 7.1 Total amount of voters: 35825 Number of cinemas: 208

5. Title: По Млечному Пути
   Rating: 7.1 Total amount of voters: 271 Number of cinemas: 38

6. Title: Без тормозов
   Rating: 6.4 Total amount of voters: 234 Number of cinemas: 64

7. Title: Кредо убийцы
   Rating: 6.2 Total amount of voters: 21232 Number of cinemas: 304

8. Title: Монстр-траки
   Rating: 6.0 Total amount of voters: 711 Number of cinemas: 182

9. Title: Снежная королева-3: Огонь и лед
   Rating: 6.0 Total amount of voters: 562 Number of cinemas: 203

10. Title: Дед Мороз. Битва магов
   Rating: 5.5 Total amount of voters: 4730 Number of cinemas: 109
```

# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)

[1] (http://www.afisha.ru/msk/schedule_cinema/)
[2] (https://www.kinopoisk.ru/)