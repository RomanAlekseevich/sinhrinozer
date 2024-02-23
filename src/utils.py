import os
from typing import List
from datetime import datetime, timedelta
from modules.files_in_the_checked_directory import FileInTheCheckedDirectory


def detecting_files_in_local_directory(path_dir: str) -> list[str]:
    """Функция создаёт список файлов находящихся  в указанной директории.
    
    :param path_dir: путь к проверяемой директории
    :type path_dir: str
    :return: список имён найденных файлов
    :rtype: list[str]
    """
    list_files_in_dir = os.listdir(path=path_dir)
    return list_files_in_dir
      
def generating_a_dict_of_files(path: str) -> dict:
    """Функция создаёт словарь хронящий в себе названия и даты последней модификации файлов
    из локальной директории выбраной для синхронизации с облочным хранилищем.
    
    :param path: путь к локальной директории.
    :type path: str
    :return: словарь с информацией о файлах.
    :rtype: dict
    """
    list_local_files = {}
    for item in detecting_files_in_local_directory(path):
        list_local_files[f"{item}"] = FileInTheCheckedDirectory(item, path)
    return list_local_files
       
def creating_a_list_of_files_to_download(list_files_in_cloud_storage: dict, local_files) -> List[str]:
    """Функция создаёт список файлов которые нужно загрузить в облочное хранилище. 
    
    :param list_files_in_cloud_storage: словарь содержащий информацию о файлах на сервере.
    :type list_files_in_cloud_storage: dict
    :param local_files: список содержащий информацию о файлах на локальном диске.
    :type local_files: list
    :return: список файлов для загрузки.
    :rtype: list
    """
    list_files_to_download = []
    for file_name in local_files:
        if file_name not in list_files_in_cloud_storage.keys():
            list_files_to_download.append(file_name)
    return list_files_to_download

def creating_a_list_of_files_to_update(files: dict, list_files_in_cloud_storage)-> List[str]:
    """Функция создайт список файлов которые были изменены и их нужно обновить 
    в облочном хранилище.
    
    :param files: словарь со всеми файлами локальной папки
    :type files: dict
    :param list_files_in_cloud_storage: словарь с файлами облачного хранилища
    :type list_files_in_cloud_storage: dict
    :return: список файлов для обновления
    :rtype: list
    """
    list_files_to_update = []
    for item in files:
        if item in list_files_in_cloud_storage.keys()\
            and (files[item].get_modification_date() > list_files_in_cloud_storage[item]):
            list_files_to_update.append(item)
    return list_files_to_update
            
def creating_a_list_of_files_to_delete(list_files_in_cloud_storage, local_files) -> List[str]:
    """Функция создаёт список файлов  в облаке, которые не найдены локально и
    их нужно удалить из облочного хранилища.
    
    :param list_files_in_cloud_storage: словарь файлов в облаке
    :type list_files_in_cloud_storage: dict
    :param local_files: список файлов на локальном диске
    :type local_files: list
    :return: список файлов для удаления
    :rtype: list
    """
    list_files_to_delete = []
    for file_name in list_files_in_cloud_storage.keys():
        if file_name not in local_files:
            list_files_to_delete.append(file_name)
    return list_files_to_delete

def convert_time_to_seconds(time: str) -> int:
    """Функция конвертирует знчение времени в формате "hh:mm:ss" в секунды.
    
    :param time: время в формате "hh:mm:ss"
    :type time: str
    :return: количество секунд
    :rtype: int
    """
    time_obj = datetime.strptime(time, '%H:%M:%S')
    result = timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)
    return result.total_seconds()