import os
import time

from datetime import datetime, timedelta, timezone

class Files_in_the_checked_directory:
    
    def __init__(self, file_name, path) -> None:
        self.name = file_name
        self.path = path
        self.file_modification_date = self.checking_the_last_modification_date_of_a_file()
           
    def get_file_path(self) -> str:
        "Функция возвращает абсолютный путь к файлу"
        # TODO: написать проверку наличия и обработку ошибок
        file_path = os.path.abspath(os.path.join(self.path, self.name))
        return file_path
    
    def get_file_name(self) -> str:
        return self.name
    
    def get_modification_date(self) -> str:
        return self.file_modification_date
     
    def checking_the_last_modification_date_of_a_file(self):
        "Функция устанавливает время последнего изменения файла"
        modification_date = datetime.fromtimestamp(os.path.getmtime(self.get_file_path()))
        return modification_date
    
    def time_format_conversion(self):
        "Функция конвертирует дату и время на локальной в дату и время в UTC"
        time_now = -time.timezone
        modification_date = int(self.checking_the_last_modification_date_of_a_file().timestamp())
        utc_time = datetime.fromtimestamp(modification_date - time_now)
        return utc_time
 