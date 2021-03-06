import requests
from datetime import datetime
import time
import pyprind
import configparser
import json

class VkWorker:
    __URL__ = 'https://api.vk.com/method/photos.getAll'
    __URL_get_users__ = 'https://api.vk.com/method/users.get'

    def __init__(self, user_id, file_token_name, foto_count=5):
        self.foto_count = foto_count
        self.file_token_name = file_token_name

        if not user_id.isdigit():
            self.user_id = self.get_id_from_scree_name(user_id)
        else:
            self.user_id = user_id

    def __get_token_from_file__(self, file_token_name):
        config = configparser.ConfigParser()
        config.read("settings.ini")
        return config['keys']['vk']

    def get_id_from_scree_name(self, screen_name):
        params = {'user_ids': screen_name,
                  'access_token': self.__get_token_from_file__(self.file_token_name),
                  'v': '5.131'
                 }

        res = requests.get(self.__URL_get_users__, params=params)
        return res.json()['response'][0]['id']

    def get_params(self):
        return {'owner_id': self.user_id,
                'access_token': self.__get_token_from_file__(self.file_token_name),
                'extended': '1',
                'count': '200',
                'v': '5.131'
                }

    def get_sort_foto_list(self):
        result = []
        res = requests.get(self.__URL__, params=self.get_params())
        for item in res.json()['response']['items']:
            for size in item['sizes']:
                if size['type'] == 'z' or size['type'] == 'x':
                    result.append({'likes': int(item['likes']['count']),
                                   'size': int(size['height'] * size['width']),
                                   'size_type': size['type'],
                                   'date': datetime.utcfromtimestamp(int(item['date'])).strftime('%y-%m-%d'),
                                   'url': size['url']
                                   })

        result = sorted(result, key=lambda x: x['size'], reverse=True)
        return sorted(result[:self.foto_count], key=lambda x: x['likes'])


class YaUploader:
    base_path = "https://cloud-api.yandex.net/"
    upload_command_path = "v1/disk/resources/upload"
    resources_command_path = "v1/disk/resources"

    def __init__(self, file_token_name: str):
        self.token = self.__get_token_from_file__(file_token_name)
        self.headers = {"Authorization": f"OAuth {self.token}",
                        "Content-Type": "application/json"}

    def __get_token_from_file__(self, file_token_name):
        config = configparser.ConfigParser()
        config.read("settings.ini")
        return config['keys']['ya']

    def upload_file_from_disk(self, file_path_from, file_path_to):
        params = {"path": file_path_to,
                  "overwrite": "true"}

        response_json = requests.get(self.base_path + self.upload_command_path, headers=self.headers,
                                     params=params).json()
        href = response_json["href"]

        response = requests.put(href, data=open(file_path_from, "rb"))
        if response.status_code == 201:
            print("???????? ????????????????")
        else:
            print(f"???????? ???? ????????????????. ???????????? ???????????????? - {str(response.status_code)}")

    def upload_file_from_inet(self, filename_on_the_ya_disk, url):
        params = {"url": url,
                  "path": filename_on_the_ya_disk}

        requests.post(self.base_path + self.upload_command_path, headers=self.headers, params=params)

    def upload_foto_list_from_vk(self, foto_list, catalog=''):
        bar = pyprind.ProgBar(len(foto_list))
        bar.title = '???????????????? ??????????: '
        count_of_foto = 0
        name_of_foto = ''
        output = []

        for foto in foto_list:
            name_of_foto = foto['likes']
            if count_of_foto == 0:
                if foto['likes'] == foto_list[count_of_foto + 1]['likes']:
                    name_of_foto = str(name_of_foto) + '(' + foto['date'] + ')'
            elif count_of_foto == len(foto_list) - 1:
                if foto['likes'] == foto_list[count_of_foto - 1]['likes']:
                    name_of_foto = str(name_of_foto) + '(' + foto['date'] + ')'
            else:
                if foto['likes'] == foto_list[count_of_foto - 1]['likes'] or foto['likes'] == \
                        foto_list[count_of_foto + 1]['likes']:
                    name_of_foto = str(name_of_foto) + '(' + foto['date'] + ')'
            count_of_foto += 1
            name_of_foto = catalog + '/' + str(name_of_foto) + '.jpg'

            self.upload_file_from_inet(name_of_foto, foto['url'])
            bar.update()
            output.append({'name': str(name_of_foto),
                           'size': foto['size_type']})
        return output

    def create_catalog(self, name):
        # ?????????????? ??????????????, ???????? ????????
        params = {'path': name,
                  'permanently': 'true'}

        res = requests.delete(self.base_path + self.resources_command_path, headers=self.headers,
                              params=params).status_code
        time.sleep(1)

        # ?????????????? ?????????? ??????????????
        params = {"path": name}
        res = requests.put(self.base_path + self.resources_command_path,
                           headers=self.headers,params=params).status_code

    def save_json_file(self, file_name, json_data):
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(json_data, file)
