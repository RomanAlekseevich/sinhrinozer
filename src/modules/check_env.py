import os
import re
import sys
import requests
from loguru import logger
from dotenv import dotenv_values


class CheckEnv:
    
    def __init__(self, file_name=".env") -> None:
        self.file_name = file_name
        self._config = self.set_config()
        self._local_directory = self._set_path_as_variable_value("local_directory")
        self._log_file = self._set_path_as_variable_value("log_file")
        self._token = None
        self._path_to_cloud_storage = None
        self._interval_between_synchronizations = self._set_tine_interval()
        
    def get_abspath(self, path: str) -> str:
        """Функция возвращяет абсолютный путь до файли или директории.

        param path: Путь до файла или деректории.
        type path: str
        return str: Абсолютный путь.
        """
        result = os.path.abspath(os.path.join(os.path.sep, *re.split(r"\\|\|/|,", path)))
        return result

    def check_path(self, path: str) -> bool:
        """Функция проверяет наличие  файла или директории по указанному пути.

        param path: Путь для проверки.
        type path: str
        return bool: True - если файл или директория есть, False - в противном случае.
        raise FileNotFoundError: Возникает если файл не найден.
        """
        if not os.path.exists(self.get_abspath(path)):
            raise FileNotFoundError(f"Файл {os.path.basename(path)} не найден.")
        else:
            return True
  
    def set_config(self) -> dict:
        """Функция загружает конфигурационный файл в словарь.
        
        return dict: Словарь с данными из .env файла.
        raise  FileNotFoundError: Возникает если файл не найден.
        """
        try:
            if  os.path.exists(self.file_name):
                return dotenv_values()
            else:
                raise FileNotFoundError(f"Файл {self.file_name} не найден.")
        except FileNotFoundError as ex:
            logger.error(ex)
            sys.exit()

    def checking_the_presence_of_a_variable_in_a_file(self, variable_name: str) -> bool:
        """Метод проверяет есть ли указанная переменная в файле.

        param variable_name: Имя переменной которую нужно проверить.
        raise KeyError: Если переменная не найдена.
        return  bool: True если переменная есть.
        """
        if variable_name in self._config:
            return True
        else:
            raise  KeyError(f'Переменная "{variable_name}" не найдена в файле')

    def _set_path_as_variable_value(self, variable_name: str) -> str:
        """Функция устанавливает путь к файлу/директории как значение для
        переменной в конструкторе класса.

        param variable_name (str): Имя переменной в конфигурационом файле.
        return str: Путь до файла/директории.
        """
        try:
            if self.checking_the_presence_of_a_variable_in_a_file(variable_name) and\
                self.check_path(self._config[variable_name]):
                return self.get_abspath(self._config[variable_name])
        except Exception as ex:
            logger.error(ex)
            sys.exit()

    def _set_tine_interval(self):
        """Функция задаёт значение в интервале времени между синхронизациями.

        return str: значение времени в формате hh:mm:ss.
        """
        if self.checking_the_presence_of_a_variable_in_a_file("interval_between_synchronizations"):
            return self._config["interval_between_synchronizations"]
  
    def create_test_request_yandex_cloud(self):
        """Функция формирует get запрос  на yandex cloud api.

        return response: Ответ от сервера.
        """
        try:
            if self.checking_the_presence_of_a_variable_in_a_file("token_yandex_disk") and\
                self.checking_the_presence_of_a_variable_in_a_file("path_on_yandex_cloud"):
                url = 'https://cloud-api.yandex.net/v1/disk/resources'
                headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json', 
                        'Authorization': f'OAuth {self._config["token_yandex_disk"]}'}
                response = requests.get(f"{url}?path={self._config['path_on_yandex_cloud']}",
                                        headers=headers)
                return response
        except Exception as ex:
            logger.error(ex)  
       
    def set_path_and_token_from_yandex_cloud(self):
        """Функция устанавливает значениея для токена и пути в облочном хранилище яндекс диска.

        raises:
            ValueError: Возникает при не привильно указаном токене.
            FileNotFoundError: Возникает при не правилько указаном пути на локальном хранилище.
            ConnectionError: Возникает при появлении проблем во время отправки запроса к яндекс диску.
        """
        try:
            response = self.create_test_request_yandex_cloud()
            if response.status_code == 200:
                self._token = self._config["token_yandex_disk"]
                self._path_to_cloud_storage = self._config["path_on_yandex_cloud"]
            elif response.status_code == 401:
                raise  ValueError("Ошибка подключения  к Яндекс.Диску. Проверьте правильность введённого токена")
            elif  response.status_code == 404:
                raise FileNotFoundError(f"Директория {self._config['path_on_yandex_cloud']} не найдена на Яндекс диске.")
            else:
                raise ConnectionError(f"{response.json()['message']}")
        except Exception as ex:
            logger.error(ex)
            sys.exit()
        
    def get_local_directory(self) -> str:
        """Функция возвращяет абсолютный путь до локальной директории файлы из которой будут
        синхронизироватся с облочным хранилищем.
        
        return str: Абсолютный путь.
        """
        return self._local_directory
    
    def get_log_file(self) -> str:
        """Возвращает полный путь до лог-файла приложения.
        
        return str: Полный путь до лог-файла.
        """
        return self._log_file

    def get_token(self) -> str:
        """Функция возвращяет  токен для авторизации в облочном хранилице.

        return str: токен
        """
        return self._token

    def get_path_to_cloud_storage(self) -> str:
        """Функция возвращяет директорию облочном хранилище для синхронизации файлов. 

        return str: директория в облочном хранилище.
        """
        return self._path_to_cloud_storage

    def get_time_interval(self):
        """Функция возвращяет значение временного интервала.
        
        return str: Время в формате "hh:mm:ss".
        """
        return self._interval_between_synchronizations
