# Copyright 2023 The OrangeBonnet <orangebonnets@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import glob
import os
import requests
import json
import datetime
from bs4 import BeautifulSoup


def create_json(appid, data):
    if not glob.glob('result/'):
        os.mkdir('result/')
    with open(f"result/{appid}.json", "w") as file:
        file.write(json.dumps(data, indent=4))
    print(f'[{appid}] Saved the result file')


def cards_scraping(soup):

    # Cards Scraping
    cards = {}
    cards_foil = {}
    for content in soup.find_all('div', class_='showcase-element-container card'):
        for card_parse in content.find_all('img', class_='element-image', loading='lazy'):
            card_name = card_parse['alt']
            card_img = card_parse['src']
            if card_name in cards.keys():
                cards_foil[card_name] = card_img
            else:
                cards[card_name] = card_img

    # Booster Pack Scraping
    booster_packs = {}
    for content in soup.find_all('div', class_='showcase-element-container booster'):
        for pack_parse in content.find_all('img', class_='element-image', loading='lazy'):
            pack_name = pack_parse['alt']
            pack_img = pack_parse['src']
            booster_packs[pack_name] = pack_img

    return cards, cards_foil, booster_packs


def badges_scraping(soup):
    badges = {}
    badges_foil = {}
    for content in soup.find_all('div', class_='showcase-element-container badge'):
        for badge in content.find_all('img', class_='element-image', loading='lazy'):
            badge_name = badge['alt']
            badge_img = badge['src']
            if len(badges) < 5:
                badges[badge_name] = badge_img
            else:
                badges_foil[badge_name] = badge_img
    return badges, badges_foil


def emoticons_scraping(soup):
    emoticons = {}
    for content in soup.find_all('div', class_='showcase-element-container emoticon'):
        for emoticon in content.find_all('img', class_='element-image', loading='lazy'):
            emoticon_name = emoticon['alt']
            if emoticon_name.find('Chat Preview') >= 0:
                continue
            emoticon_img = emoticon['src']
            emoticons[emoticon_name] = emoticon_img
    return emoticons


def backgrounds_scraping(soup):
    backgrounds = {}
    for content in soup.find_all('div', class_='showcase-element-container background'):
        for background in content.find_all('img', loading='lazy'):
            background_name = background['alt']
            background_img = background['src']
            backgrounds[background_name] = background_img[:-13]
    return backgrounds


def collect_data(appid, soup):
    date = datetime.datetime.now()
    unix_time = int(datetime.datetime.timestamp(date) * 1000)
    data = {'appid': appid,
            'time': unix_time}
    # Game not found!
    if soup.find('p', string='Game not found!'):
        data['cards'] = False
    else:
        data['cards'] = True
        app_name = soup.find('div', class_='game-title').getText()
        app_img = soup.find('img', class_='game-image').get('src')
        cards, cards_foil, booster_packs = cards_scraping(soup)
        badges, badges_foil = badges_scraping(soup)
        emoticons = emoticons_scraping(soup)
        backgrounds = backgrounds_scraping(soup)
        details = {'app_name': app_name, 'app_img': app_img,
                   'cards': cards, 'cards_foil': cards_foil, 'booster_packs': booster_packs,
                   'badges': badges, 'badges_foil': badges_foil,
                   'emoticons': emoticons,
                   'backgrounds': backgrounds}
        data['details'] = details
    return data


def start_scraping(appid):
    payload = f'gamepage-appid-{str(appid)}'
    r = requests.get('https://www.steamcardexchange.net/index.php?' + payload)
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        data = collect_data(appid, soup)
        create_json(appid, data)
    else:
        print(f'[{appid}] Website error status code - {r.status_code}')
        pass


if __name__ == '__main__':
    print('Enter AppID')
    start_scraping(input())