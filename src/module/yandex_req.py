# Чтобы обеспечить дальнейшее расширение программы для работы с другими файловыми сервисами,
# логика работы с конкретным облачным хранилищем должна быть вынесена в отдельный класс и файл. 
# Конструктор этого класса должен принимать токен доступа и путь к существующей папке для 
# хранения резервных копий в удалённом хранилище.

import json
import requests
import re
import os

from datetime import datetime
from loguru import logger


class Yandex_disk():
    
    def __init__(self, token: str, path_to_the_folder: str) -> None:
        self.token = token
        self.path_to_the_folder = path_to_the_folder
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {self.token}'}

    def load(self, path, overwrite=False):
        'Метод для загрузки файла в хранилище'
        try:
            file_name = self.get_name_in_path(path)
            req = self.get_link_for_download( file_name, overwrite)
            with open(path, 'rb') as file:
                requests.put(req['href'], files={'file':file})
            logger.info(f"Файл {file_name} успешно записан.")
        except Exception as ex:
             logger.error(f"При записи файла '{file_name}'возникла ошибка: {ex}")
    
    def reload(self, path, overwrite=True):
        'Метод для перезаписи файла в хранилище'
        try:
            file_name = self.get_name_in_path(path)
            req = self.get_link_for_download(file_name, overwrite)
            with open(path, 'rb') as file:
                requests.put(req['href'], files={'file':file})
            logger.info(f"Файл {file_name} успешно перезаписан.")
        except Exception as ex:
            logger.error(f"При перезаписи файла '{file_name}' возникла ошибка: {ex}")
    
    def delete(self, file_name, permanently="false"):
        'Метод для удаления файла из хранилища'
        try:
            response = requests.delete(f'{self.url}?path={self.path_to_the_folder}/{file_name}&permanently={permanently}', headers=self.headers)
            if response.status_code not in (200, 202, 204):
                raise Exception(f"{response.status_code} {response.json()['message']}")
            else:
                logger.info(f"Файл {file_name} успешно удалён.")
        except Exception as ex:
            logger.error(f"При удалении файла '{file_name}' возникла ошибка: {ex}")
    
    def get_info(self):
        'Метод для получения информации о хранящихся в удалённом хранилище файлах'
        try:
            response = requests.get(f'{self.url}?path={self.path_to_the_folder}&fields=_embedded.items.name%2C%20_embedded.items.modified%20', headers=self.headers)
            if response.status_code == 200:
                result = json.loads(response.content)
                list_files_in_cloud_storage = {}
                for i in result['_embedded']['items']:
                    list_files_in_cloud_storage[i['name']] = datetime.fromtimestamp(datetime.strptime(i['modified'], '%Y-%m-%dT%H:%M:%S%z').timestamp())
                return list_files_in_cloud_storage
            else:
                raise Exception(f"{response.status_code} {response.json()['message']}")
        except Exception as ex:
            logger.error(f"При получении информации о файлах в удалённом хранилище возникла ошибка: {ex}")
        
    def get_link_for_download(self, file_name: str, overwrite=False):
            req = requests.get(f'{self.url}/upload?path={self.path_to_the_folder}/{file_name}&overwrite={overwrite}', headers=self.headers)
            if req.status_code != 200:
                raise Exception(f"{req.status_code} {req.json()['message']}")
            else:
                return req.json()
            
    def get_name_in_path(self, path: str) -> str:
        name = re.split(r"\\|/", path)[-1]
        return name