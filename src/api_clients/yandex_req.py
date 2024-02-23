import json
import requests
import os

from datetime import datetime
from loguru import logger
from typing import Optional


class YandexDisk:
    """Класс для работы с api  Яндекс.Диска.
    
    Args:
        token (str): Токен доступа к Яндекс.Диску.
        path_to_the_folder (str): Директория в облочном хранилище.
        
    Attributes:
        token (str): Токен доступа к Яндекс.Диску.
        path_to_the_folder (str): Директория в облочном хранилище.
        url (str): Базовый урл для запросов API Яндекс.Диска.
        headers (dict): Заголовки для запросов.
    """
    
    def __init__(self, token: str, path_to_the_folder: str) -> None:
        self.token = token
        self.path_to_the_folder = path_to_the_folder
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': f'OAuth {self.token}'}

    def _load_to_cloud(self, path: str, file_name: str,overwrite: bool) -> None:
        req = self.get_link_for_download( file_name, overwrite)
        with open(path, 'rb') as file:
            requests.put(req['href'], files={'file':file})

    def load(self, path) -> None:
        """Метод для загрузки файла в хранилище.
        
        :param path: Путь к файлу на локальной машине.
        :type path: str
        """
        try:
            file_name = os.path.basename(path)
            self._load_to_cloud(path, file_name, False)
            logger.info(f"Файл {file_name} успешно записан.")
        except Exception as ex:
             logger.error(f"При записи файла '{file_name}'возникла ошибка: {ex}")
      
    def reload(self, path: str) -> None:
        """Метод для перезаписи файла в хранилище
        
        :param path: Путь к файлу на локальной машине.
        :type path: str
        """
        try:
            file_name = os.path.basename(path)
            self._load_to_cloud(path, file_name, True)
            logger.info(f"Файл {file_name} успешно перезаписан.")
        except Exception as ex:
             logger.error(f"При перезаписи файла '{file_name}'возникла ошибка: {ex}")

    def delete(self, file_name: str, permanently: str = "false") -> None:
        """Метод для удаления файла из хранилища.
        
        :param file_name: Название файла.
        :type file_name: str
        :param permanently: Флаг определяющий, нужно ли удалить файл 
                            полностью или отправить его в корзину.  
                            По умолчанию - false.
        """
        try:
            response = requests.delete(f'{self.url}?path={self.path_to_the_folder}/{file_name}&permanently={permanently}', 
                                       headers=self.headers)
            if response.status_code not in (200, 202, 204):
                logger.error(f"{response.status_code} {response.json()['message']}")
            else:
                logger.info(f"Файл {file_name} успешно удалён.")
        except Exception as ex:
            logger.error(f"При удалении файла '{file_name}' возникла ошибка: {ex}")
    
    def get_info(self) -> Optional[dict]:
        """Метод для получения информации о хранящихся в удалённом хранилище файлах

        return dict: словарь с названиями файлов и датой их последней модификации.
        """
        try:
            response = requests.get(f'{self.url}?path={self.path_to_the_folder}&fields=_embedded.items.name%2C%20_embedded.items.modified%20', headers=self.headers)
            if response.status_code == 200:
                result = json.loads(response.content)
                list_files_in_cloud_storage = {}
                for i in result['_embedded']['items']:
                    list_files_in_cloud_storage[i['name']] = datetime.fromtimestamp(datetime.strptime(i['modified'], '%Y-%m-%dT%H:%M:%S%z').timestamp())
                return list_files_in_cloud_storage
            else:
                logger.error(f"{response.status_code} {response.json()['message']}")
        except Exception as ex:
            logger.error(f"При получении информации о файлах в удалённом хранилище возникла ошибка: {ex}")
        
    def get_link_for_download(self, file_name: str, overwrite: bool) -> Optional[dict]:
        """Функция отправляет get запрос на yandex cloud api  для получения ссылки  
        на загрузку файла.

        :param  file_name: Название файла.
        :type   file_name: str
        :return: Словарь с данными о ссылке на загрузку файла.
        """
        try:    
            req = requests.get(f'{self.url}/upload?path={self.path_to_the_folder}/{file_name}&overwrite={overwrite}', headers=self.headers)
            if req.status_code != 200:
                logger.error(f"{req.status_code} {req.json()['message']}")
            else:
                return req.json()
        except Exception as ex:
            logger.error(ex)
