import pandas as pd


class SplitAnalyzer:
    COST_COL = "Cost"
    DATE_COL = "Date"
    CATEGORY_COL = "Category"

    def __init__(self, data_file_path):
        self.df = pd.read_csv(data_file_path)
        self.df.loc[:, self.DATE_COL] = pd.to_datetime(self.df[self.DATE_COL])
        self.df.loc[:, self.COST_COL] = pd.to_numeric(self.df[self.COST_COL], errors="coerce").fillna(0)

    def get_month_balance(self, month, year):
        month_mask = self.df[self.DATE_COL].map(lambda x: x.month == month and x.year == year)
        categories_sums = self.df[month_mask].groupby(self.CATEGORY_COL).sum()
        return self.df[month_mask][self.COST_COL].sum(), categories_sums[self.COST_COL]

