import os
import requests

SUCCESS_CODE = 1
FAIL_CODE = 0


class SplitDownloadAPI:
    def __init__(self, api_key):
        self.header = {"Authorization": f"Bearer {api_key}"}

    def download_group(self, group_num, out_path):
        url = f"https://www.splitwise.com/api/v3.0/export_group/{group_num}.csv"
        try:
            respond = requests.get(url, headers=self.header)
        except requests.ConnectionError or requests.HTTPError:
            respond = None
            pass
            # todo handle
        if respond:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(respond.content.decode("utf-8"))
            return SUCCESS_CODE
        else:
            return FAIL_CODE


DATA_DIR = os.path.join(os.path.curdir, "data", "to_process")

