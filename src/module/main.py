import os
import re
import time
import requests
import json
from datetime import datetime, timedelta, timezone

from dotenv import dotenv_values
from loguru import logger

from yandex_req import Yandex_disk
from files_in_the_checked_directory import Files_in_the_checked_directory


config = dotenv_values()
TOKEN = config['TOKEN']
path_to_the_synchronized_folder = config['LOCAL_DERECTORY']
directory_in_cloud_storage = config['directory_in_cloud_storage']
log_file = os.path.abspath(os.path.join(os.path.sep, *re.split(r"\\|\|/|,", config['log_file'])))

logger.add(f'{log_file}', format="sinhrinozer {time:YYYY-MM-DD HH:mm:ss,SSS} {level} {message}", rotation='1 MB', compression='zip')

interval_between_synchronizations = config["interval_between_synchronizations"]



def get_local_dir(path: str) -> str:
    try:
        result = os.path.abspath(os.path.join(os.path.sep, *re.split(r"\\|\|/|,", path)))
        if os.path.exists(result):
            
            return result
        else:
            raise FileNotFoundError(f"Директория {path} не существует или указана не верно!")
    except Exception as ex:
        logger.error(ex)

def detecting_files_in_local_directory(path_dir: str) -> list[str]:
    list_files_in_dir = os.listdir(path=path_dir)
    return list_files_in_dir
      
def generating_a_dict_of_files(path: str) -> dict:
    list_local_files = {}
    for item in detecting_files_in_local_directory(path):
        list_local_files[f"{item}"] = Files_in_the_checked_directory(item, path)
    return list_local_files
     
def checking_for_file_availability_in_cloud_storage(file_name: str, list_files_in_cloud_storage: dict) -> bool:
    result = False
    if file_name in list_files_in_cloud_storage.keys():
        result = True
    return result
        
def creating_a_list_of_files_to_download(list_files_in_cloud_storage: dict, local_files):
    list_files_to_download = []
    for file_name in local_files:
        if file_name not in list_files_in_cloud_storage.keys():
            list_files_to_download.append(file_name)
    return list_files_to_download

def creating_a_list_of_files_to_update(files: dict, list_files_in_cloud_storage):
    list_files_to_update = []
    for item in files:
        if checking_for_file_availability_in_cloud_storage(item, list_files_in_cloud_storage) and (files[item].get_modification_date() > list_files_in_cloud_storage[item]):
            list_files_to_update.append(item)
    return list_files_to_update
            
def creating_a_list_of_files_to_delete(list_files_in_cloud_storage, local_files):
    list_files_to_delete = []
    for file_name in list_files_in_cloud_storage.keys():
        if file_name not in local_files:
            list_files_to_delete.append(file_name)
    return list_files_to_delete

def convert_time_to_seconds(time: str):
    time_obj = datetime.strptime(time, '%H:%M:%S')
    result = timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)
    return result.seconds

if __name__ == "__main__":
    count = 0
    path = get_local_dir(path_to_the_synchronized_folder)
    if path:
        timer = convert_time_to_seconds(interval_between_synchronizations)
        logger.info(f"Программа синхронизации файлов начинает работу с директорией {path}.")
        while count < 2:
            local_files = detecting_files_in_local_directory(path)
            if not local_files:
                time.sleep(timer)
                continue
            else:
                files = generating_a_dict_of_files(path)
            try:
                connect = Yandex_disk(path_to_the_folder=directory_in_cloud_storage, token=TOKEN)
                get_info = connect.get_info()
            except Exception as ex:
                logger.error(ex)
            else:
                download_list = creating_a_list_of_files_to_download(get_info, local_files)
                if download_list:
                    for i in download_list:
                        connect.load(files[i].get_file_path())
            
                update_list = creating_a_list_of_files_to_update(files, get_info)
                if update_list:
                    for i in update_list:
                        connect.reload(files[i].get_file_path())

                delete_list = creating_a_list_of_files_to_delete(get_info, local_files)
                if delete_list:
                    for file_name in delete_list:
                        connect.delete(file_name)
            print("скрипт завершился")
            count += 1
            time.sleep(timer)
