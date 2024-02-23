import time

from dotenv import dotenv_values
from loguru import logger

from api_clients.yandex_req import YandexDisk
from modules.check_env import CheckEnv
from utils import *


config = CheckEnv(".env")
config.set_path_and_token_from_yandex_cloud()
TOKEN = config.get_token()
local_path = config.get_local_directory()
directory_in_cloud_storage = config.get_path_to_cloud_storage()
interval_between_synchronizations = config.get_time_interval()
log_file = config.get_log_file()

logger.add(f'{log_file}', format="synchroniser {time:YYYY-MM-DD HH:mm:ss,SSS} {level} {message}", rotation='1 MB', compression='zip')


if __name__ == "__main__":
    count = 0
    if local_path:
        timer = convert_time_to_seconds(interval_between_synchronizations)
        logger.info(f"Программа синхронизации файлов начинает работу с директорией {local_path}.") 
        connect = YandexDisk(path_to_the_folder=directory_in_cloud_storage, token=TOKEN)   
           
        while count < 2:
            local_files = detecting_files_in_local_directory(local_path)
            files = generating_a_dict_of_files(local_path)
 
            get_info = connect.get_info()
            if get_info is None:
                continue
         
         
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
