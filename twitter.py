# As the program is intended to run on CPU, 
# it is not recommended to run on Google Colab.
# Please run on local computer.
# 
# To install dependencies,
# !python -m pip install tqdm pandas requests orjson
#
# DataFile must be included in "./dataset/(Dataset 4) Drug Use Tweets/"

import pandas as pd
from tqdm import tqdm
import multiprocessing
import ctypes
import sys
import numpy as np
import os

_MessageBox = ctypes.windll.user32.MessageBoxW
def alert(message, title="Retrieving data from twitter url"):
    return _MessageBox(None, message, title, 0x00)

def get_vxtweet(url:str) -> dict|None:
    """Get Data from api.vxtwitter

    reference: [https://github.com/dylanpdx/BetterTwitFix](https://github.com/dylanpdx/BetterTwitFix)

    @Args:
        url (str): twitter url. It must be valid userename and twit code.

    @Returns:
        dict|None: data of tweet if it is valid. None for else.
    """
    from urllib.parse import urlparse
    import requests
    _url = urlparse(url)
    url = url.replace(_url.hostname, 'api.vxtwitter.com')
    resp = requests.get(url)
    return resp.text

def resp_to_dict(resp_text:str) -> dict | None:
    import orjson as json
    try:
        jsonData = json.loads(resp_text)
        return jsonData
    except json.JSONDecodeError:
        return {}
    
SAVE_DIR = "Dataset_3_processed.csv" if sys.argv.__len__() == 1 else sys.argv[1]
if __name__ == "__main__":
    multiprocessing.freeze_support()
    max_cpu_count = multiprocessing.cpu_count()
    print(f"As this computer has {max_cpu_count} cpus, it will use {max(max_cpu_count - 2, 1)} cpus for worker.")
    # There is Memory Comsumption Error... Maybe?   
    df = pd.concat([pd.read_csv("./dataset/(Dataset 4) Drug Use Tweets/Main_data.csv"), pd.read_csv("./dataset/(Dataset 4) Drug Use Tweets/Other_data.csv")]).reindex()
    for i, url_df in enumerate(np.array_split(df.url, max(max_cpu_count - 2, 1) * 5)):
        fileName = f"Data_tmp_{str(i+1).zfill(3)}.csv"
        if fileName in os.listdir(): # 이미 처리된 데이터는 빼고 처리
            continue
        
        print(f"work {i+1} / {max(max_cpu_count - 2, 1) * 5}")
        with multiprocessing.Pool(max(max_cpu_count - 2, 1)) as pool:
            print("retrive data from twitter")
            tqdm_d = list(tqdm(pool.imap(get_vxtweet, url_df), total=url_df.shape[0]))
            print("processing data to dict")
            tqdm_d = tqdm(pool.imap(resp_to_dict, tqdm_d), total=url_df.shape[0])
            data = pd.DataFrame.from_records(list(tqdm_d))
            data.to_csv(fileName, index=False)
            df = pd.concat([df, data])
    df.to_csv(SAVE_DIR)
    alert(f"All data has been saved to '{SAVE_DIR}'")