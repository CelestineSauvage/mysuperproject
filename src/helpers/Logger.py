from datetime import datetime

class Logger:
    ### Class for logging the HTTP APIs call and the scraping

    def __init__(self):
        self.logs_lst = []

    def start_session(self):
        time = Logger.__get_time()
        message = "Session starts"
        Logger.__logging(time, message, self.logs_lst)

    def end_session(self):
        time = Logger.__get_time()
        message = "Session ends."
        Logger.__logging(time, message, self.logs_lst)

    def start_scraping(self, position):
        time = Logger.__get_time()
        message = f"Scraping attempt with the key word: '{position}'... "
        Logger.__logging(time, message, self.logs_lst)

    def scraping_result(self, df):
        time = Logger.__get_time()
        message = f"....successfully implemented. Number of records found: {len(df)}"
        Logger.__logging(time, message, self.logs_lst)

    def scraping_result_final(self, df):
        time = Logger.__get_time()
        message = f"Full scraping is executed. The raw data dump file contains {len(df)} records.\n" \
                  f"Number of unique records is {df['job_id'].nunique()}."
        Logger.__logging(time, message, self.logs_lst)

    def data_formatted(self, df):
        time = Logger.__get_time()
        message = f"Data dump is formatted:\n {df.info()}"
        Logger.__logging(time, message, self.logs_lst)

    def error_occurs(self, error):
        time = Logger.__get_time()
        message = f"{error} occurs"
        Logger.__logging(time, message, self.logs_lst)
        
    @staticmethod
    def __get_time() -> str:
        return datetime.now().strftime('%d-%m-%Y, %H:%M:%S')

    @staticmethod
    def __logging(time, message, logs_lst):
        log = (time, message)
        logs_lst.append(log)
        print(time + ': ' + message)