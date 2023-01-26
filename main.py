import json
import os.path

import requests
from bs4 import BeautifulSoup

from auth import params, headers


def save_to_html(html, file_name):
    with open(f'{file_name}.html', 'w', encoding='utf-8') as file:
        file.write(html)


def main():
    result = []
    if not os.path.exists('data/'):
        os.mkdir('data')
    # save_to_html(response.text, 'index')
    for i in range(1, 5):
        if not os.path.exists(f'data/{i}/'):
            os.mkdir(f'data/{i}')
        params['currentpage'] = i
        response = requests.get(
            'https://www.truckscout24.de/transporter/gebraucht/kuehl-iso-frischdienst/renault',
            params=params,
            headers=headers,
        )
        soup = BeautifulSoup(response.text, 'lxml')
        card = soup.find('div', class_='ls-elem')
        title = card.find('h2', class_='ls-makemodel').text
        href = 'https://www.truckscout24.de'+card.find('a', {'data-item-name': 'detail-page-link'}).get('href')
        try:
            price = int(card.find('span', class_='sc-highlighter-4').text.strip()[2:-2].replace('.', '').strip())
        except ValueError:
            price = 0
        r = requests.get(href, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')

        try:
            power = int(soup.find('div', text='Leistung').find_next_sibling('div').text.split('kW')[0].strip())
        except AttributeError:
            power = 0

        try:
            color = soup.find('div', text='Farbe').find_next_sibling('div').text.strip()
        except AttributeError:
            color = ''

        try:
            mileage = int(soup.find('div', text='Kilometer').find_next_sibling('div').text.replace('km', '').replace('.', '').strip())
        except AttributeError:
            mileage = 0

        try:
            desc = soup.find('div', class_='short-description').text.replace(' ', '').replace('\r', '')\
                .replace('\n', ' ').strip()
        except AttributeError:
            desc = ''

        try:
            images = soup.find('div', class_='as24-carousel__container').find_all('div', class_='as24-carousel__item')[:3]
            for img_i, image in enumerate(images):
                src = image.find('img').get('data-src')
                image_r = requests.get(src)
                with open(f'data/{i}/{img_i}.jpg', 'wb') as file:
                    file.write(image_r.content)
        except AttributeError:
            print(f'no images {href}')

        result.append(
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

    with open('data/data_final.json', 'w', encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
