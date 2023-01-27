import json
import os.path

import requests
from bs4 import BeautifulSoup

from auth import params, headers, MAIN_URL


def save_to_html(html, file_name):
    with open(f'{file_name}.html', 'w', encoding='utf-8') as file:
        file.write(html)


def get_data():
    result = []
    i = 1
    if not os.path.exists('data/'):  # создание директории data
        os.mkdir('data')

    while True:  # основной цикл
        params['currentpage'] = i
        response = requests.get(MAIN_URL, params=params, headers=headers)  # получение ответа от страницы MAIN_URL из файла auth
        soup = BeautifulSoup(response.text, 'lxml')

        card = soup.find('div', class_='ls-elem')
        if not card:  # проверка на наличие объявлений на странице
            print('[INFO] Data collected.')
            break

        if not os.path.exists(f'data/{i}/'):  # создание директорий под каждый id
            os.mkdir(f'data/{i}')

        title = card.find('h2', class_='ls-makemodel').text
        href = 'https://www.truckscout24.de' + card.find('a', {'data-item-name': 'detail-page-link'}).get('href')

        try:
            price = int(card.find('span', class_='sc-highlighter-4').text.strip()[2:-2].replace('.', '').strip())
        except ValueError:
            price = 0

        href_response = requests.get(href, headers=headers)  # получение ответа от страницы объявления (href)
        soup = BeautifulSoup(href_response.text, 'lxml')

        try:
            power = int(soup.find('div', text='Leistung').find_next_sibling('div').text.split('kW')[0].strip())
        except AttributeError:
            power = 0

        try:
            color = soup.find('div', text='Farbe').find_next_sibling('div').text.strip()
        except AttributeError:
            color = ''

        try:
            mileage = int(
                soup.find('div', text='Kilometer').find_next_sibling('div').text.replace('km', '').replace('.',
                                                                                                           '').strip())
        except AttributeError:
            mileage = 0

        try:
            desc = soup.find('div', class_='short-description').text.replace(' ', '').replace('\r', '') \
                .replace('\n', ' ').strip().replace(' ', '').strip()
        except AttributeError:
            desc = ''

        try:
            images = soup.find('div', class_='as24-carousel__container').find_all('div', class_='as24-carousel__item')[
                     :3]  # отбор первых трех изображений
            for img_i, image in enumerate(images):
                src = image.find('img').get('data-src')
                image_r = requests.get(src)
                with open(f'data/{i}/{img_i}.jpg', 'wb') as file:  # сохранение изображений
                    file.write(image_r.content)
        except AttributeError:
            print(f'[ERROR] No images {href}.')

        result.append(  # наполнение списка собранной информацией
            {
                'id': i,
                'href': href,
                'title': title,
                'price': price,
                'mileage': mileage,
                'color': color,
                'power': power,
                'description': desc
            }
        )
        i += 1  # увеличение i (номера страницы)

    with open('data/data_final.json', 'w', encoding='utf-8') as file:  # сохранение
        json.dump(result, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    get_data()
