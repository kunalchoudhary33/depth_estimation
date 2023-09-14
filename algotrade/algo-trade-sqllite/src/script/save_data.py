import py_mysql
from datetime import date
import logging

logging.basicConfig(level=logging.DEBUG)
data_to_csv = "src/data/"

class Save_Data():

    def __init__(self):
        self.py_mysql_obj = py_mysql.Mysql_Server()
        self.today = date.today()

    def save_to_csv(self):
        data = self.py_mysql_obj.fetch_ticks()
        if(len(data)>0):
            file_name = str(data['date'][0]).split(" ")[0] 
            data.to_csv(data_to_csv+str(self.today)+".csv", index=False, header=True)
            logging.info(" Previous data saved to : "+data_to_csv+str(file_name)+".csv")
            self.truncate_table()
        else:
            logging.info(" Table empty and no data saved. Although ready for fresh new entries.!!")

    def truncate_table(self):
        self.py_mysql_obj.truncate_table()
        logging.info(" Table Truncated and cleaned for fresh new entries !!!!!!")


def main():
    save_data = Save_Data()
    save_data.save_to_csv()


if __name__=="__main__":
    main()