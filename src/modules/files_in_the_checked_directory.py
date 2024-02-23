import os
import time

from datetime import datetime, timedelta, timezone

class FileInTheCheckedDirectory:
    """Класс для работы с лочальными файлами в директории.
    
    Args:
        file_name (str): Имя файла.
        path (str): путь к локальной директории.
        
    Attributes:
        file_name (str): Имя файла.
        path (str): путь к локальной директории.
        file_modification_date (datetime): дата и время последней модификации файла.
    """
    
    def __init__(self, file_name, path) -> None:
        self.name = file_name
        self.path = path
        self.file_modification_date = self.set_the_last_modification_date_of_a_file()
           
    def get_file_path(self) -> str:
        """Функция возвращает абсолютный путь к файлу.

        return: path
        rtype: str
        """
        file_path = os.path.abspath(os.path.join(self.path, self.name))
        return file_path
    
    def get_file_name(self) -> str:
        """Геттер для получении имени файла.
        
        return: name
        rtype: str
        """
        return self.name
    
    def get_modification_date(self) -> str:
        """Геттер для получения даты последнего изменения файла. 
        
        return: file_modification_date
        rtype: datetime
        """
        return self.file_modification_date
     
    def set_the_last_modification_date_of_a_file(self):
        """Функция устанавливает время последнего изменения файла.

        return: дату и время последней модификации.
        rtype: datetime
        """
        modification_date = datetime.fromtimestamp(os.path.getmtime(self.get_file_path()))
        return modification_date
    
    def time_format_conversion(self):
        "Функция конвертирует дату и время на локальной в дату и время в UTC"
        time_now = -time.timezone
        modification_date = int(self.checking_the_last_modification_date_of_a_file().timestamp())
        utc_time = datetime.fromtimestamp(modification_date - time_now)
        return utc_time
 