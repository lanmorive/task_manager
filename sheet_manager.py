from google.oauth2.service_account import Credentials
import gspread
import pandas as pd


class SheetManager:
    """
    Класс для работы с Google Sheets
    """

    def __init__(self,SPREADSHEET_ID):

        creds = Credentials.from_service_account_file(
            "single-arcadia-435019-h6-4e59ee50c184.json",
            scopes=["/etc/secrets/single-arcadia-435019-h6-4e59ee50c184.json"])
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(SPREADSHEET_ID).worksheet("Tasks")
        

    def add_task(self,task, date,prioirity):
        """
        Adds a task to the Google Sheet."
        """
        id_ = len(self.sheet.get_all_records())
        self.sheet.append_row([id_,task, prioirity, date,'Активно'])
        return id_
    
    def get_active_tasks(self):
        """
        Получаем все активные таски
        """
        rows = self.sheet.get_all_records()
        return pd.DataFrame(rows).query('status == "Активно"').sort_values(by='priority', ascending=False)
    
    def close_task(self, id_):
        """
        Закрывает задачу
        """
        try:
            rows = self.sheet.get_all_records()
            df = pd.DataFrame(rows)
            row_data = df[df['id'] == int(id_)]

            if row_data.empty:
               return 'Задача не найдена'
            
            if row_data['status'].values[0] == 'Закрыто':
               return 'Задача уже закрыта'
            
            index_in_df = row_data.index[0]
            row_in_sheet = index_in_df + 2
            self.sheet.update_cell(row_in_sheet, 5, 'Закрыто')
            return 'Задача закрыта'
        except:
            return 'Неверный номер задачи'
