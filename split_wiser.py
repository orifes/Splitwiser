import json

from tele_alert import send_message, send_messages
from analyze_split import SplitAnalyzer
from get_splitwise_data import SplitDownloadAPI, SUCCESS_CODE
from install import get_config, SPLIT_GROUP_KEY, THRESHOLD_KEY, CAT_KEY, SPLIT_API_KEY
import os.path as path
import time
import datetime as dt
import calendar
import os
import pickle

CONFIG_DICT = None


class SplitWiser:
    PICKLE_ALERT = "alerted"
    PICKLE_EXPENSE = "expense"
    DATA_FILE = "group_data.csv"
    LOG_FILE = "split_log.txt"
    DAY_INX, MONTH_INX, YR_INX = 0, 1, 2
    LAST_DAY_INX = 1
    TOTAL_TXT = "Total"
    CAT_PATTERN = "under {} category."
    DOWN_RESULT_FIELD = "Data Download"
    TIME_FORMAT = "%H:%M"

    def __init__(self, api_key, output_dir, date):
        self.__downloader = SplitDownloadAPI(api_key)
        self.__analyzer = None
        self.__output_dir = output_dir
        self.__data_path = os.path.sep.join([self.__output_dir, self.DATA_FILE])
        self.__date = date
        self.__last_day = calendar.monthrange(date[self.YR_INX], date[self.MONTH_INX])[self.LAST_DAY_INX]
        self.__days_left = self.__last_day - date[self.DAY_INX]
        self.__log_file = open(os.path.sep.join([self.__output_dir, self.LOG_FILE]), "a+")
        self._log_data("DATE", f"{date[self.DAY_INX]}-{date[self.MONTH_INX]}-{date[self.YR_INX]}")
        self._log_data("TIME", time.strftime(self.TIME_FORMAT))
        if self.__date[self.DAY_INX] == 1:
            self.__reset_alert_hist()

    def _log_data(self, key, value):
        self.__log_file.write(f"{key}={value}\t")

    def download_try(self, group_num):
        exit_code = self.__downloader.download_group(group_num, self.__data_path)
        self._log_data(self.DOWN_RESULT_FIELD, exit_code)
        if exit_code == SUCCESS_CODE:
            self.__analyzer = SplitAnalyzer(self.__data_path)

    def __reset_alert_hist(self):
        self.__update_alert_history(False, 0)

    def __threshold_msg(self, expenses, category_addition, sent=False, past_exp=0):
        if not sent:
            new_msg = ["Attention!", f"You've reached the monthly expenses alert threshold! "
                                     f"You spent {int(expenses)} {category_addition}"]
            if self.__days_left:
                new_msg.append(f"There are {self.__days_left} more days in this month.Spend Wisely!")
            send_messages(new_msg)
        else:
            if expenses > past_exp:
                update_msg = f"You continued spending after threshold reached, you spent {expenses}. SPEND WISELY!"
                send_message(update_msg)

    def __alert_history(self):
        if os.path.exists(self.PICKLE_ALERT) and os.path.exists(self.PICKLE_EXPENSE):
            sent = pickle.load(open(self.PICKLE_ALERT, "rb"))
            expenses = pickle.load(open(self.PICKLE_EXPENSE, "rb"))
        else:
            sent = False
            expenses = 0
        return sent, expenses

    def __update_alert_history(self, sent, expenses):
        pickle.dump(sent, open(self.PICKLE_ALERT, "wb"))
        pickle.dump(expenses, open(self.PICKLE_EXPENSE, "wb"))

    def check_thresholds(self, tot_threshold, cats_thresholds):
        monthly_exp, category_dist = self.__analyzer.get_month_balance(self.__date[self.MONTH_INX],
                                                                       self.__date[self.YR_INX])
        sent = False
        alerted, past_exp = self.__alert_history()
        if monthly_exp >= tot_threshold:
            sent = past_exp < monthly_exp
            self.__threshold_msg(monthly_exp, self.TOTAL_TXT, alerted, past_exp)

        for category in cats_thresholds:
            cat_expenses = category_dist.get(category)
            if cat_expenses and cat_expenses >= cats_thresholds[category]:
                sent = True
                self.__threshold_msg(cat_expenses, self.CAT_PATTERN.format(category))
        self.__update_alert_history(sent, monthly_exp)
        return monthly_exp, category_dist, sent

    @staticmethod
    def __sum_msg(monthly_exp, cat_expense):
        msg = ["Hi! tomorrow is a new month! Hope you had a great one! Here's your monthly summary:",
               f"Total spent: {monthly_exp}. And by categories:"]
        for cat in cat_expense.index:
            if cat and cat_expense[cat]:
                msg.append(f"{cat}:{cat_expense[cat]}")
        send_messages(msg)

    def run_analyzer(self, month_threshold, categories_thresholds):
        if self.__analyzer:
            monthly_exp, category_dist, sent = self.check_thresholds(month_threshold, categories_thresholds)
            self._log_data("ALERTED", str(sent))
            if self.__date[self.DAY_INX] == self.__last_day:
                if sent:
                    send_message("But it's the last day of the month, so... you'll get your summary,"
                                 "and pay another attention to your big spending !")
                self.__sum_msg(monthly_exp, category_dist)
                self._log_data("HAD_SUMMARY", "True")

    def __del__(self):
        self.__log_file.write("END\n")
        self.__log_file.close()


if __name__ == '__main__':
    OUTPUT_FILE = "data.csv"
    today = dt.date.today().day, dt.date.today().month, dt.date.today().year
    process_dir = path.join(".", "data")
    data_path = process_dir + path.sep + OUTPUT_FILE
    try:
        CONFIG_DICT = get_config()
        EXPENSES_THRESHOLD = CONFIG_DICT[THRESHOLD_KEY]
        CATEGORIES_THRESHOLD = CONFIG_DICT[CAT_KEY]
        API_KEY = CONFIG_DICT[SPLIT_API_KEY]
        GROUP_NUM = CONFIG_DICT[SPLIT_GROUP_KEY]
        split_wiser = SplitWiser(API_KEY, process_dir, today)
        split_wiser.download_try(GROUP_NUM)
        split_wiser.run_analyzer(EXPENSES_THRESHOLD, CATEGORIES_THRESHOLD)
    except KeyError or IOError:
        print("Invalid config file.")
        exit(-1)
