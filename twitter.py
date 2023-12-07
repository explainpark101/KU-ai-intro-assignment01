# As the program is intended to run on CPU, 
# it is not recommended to run on Google Colab.
# Please run on local computer.
# 
# To install dependencies,
# !python -m pip install tqdm pandas requests orjson

import pandas as pd
from tqdm import tqdm
import multiprocessing
import ctypes
import sys

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
    import orjson as json
    _url = urlparse(url)
    url = url.replace(_url.hostname, 'api.vxtwitter.com')
    resp = requests.get(url)
    try:
        jsonData = json.loads(resp.text)
        return jsonData
    except json.JSONDecodeError:
        return None
    
SAVE_DIR = "Dataset_3_processed.csv" if sys.argv.__len__() == 1 else sys.argv[1]
if __name__ == "__main__":
    multiprocessing.freeze_support()
    print(f"As this computer has {multiprocessing.cpu_count()} cpus, it will use {max(multiprocessing.cpu_count() - 2, 1)} cpus for worker.")

    df = pd.concat([pd.read_csv("./dataset/(Dataset 4) Drug Use Tweets/Main_data.csv"), pd.read_csv("./dataset/(Dataset 4) Drug Use Tweets/Other_data.csv")]).reindex()
    with multiprocessing.Pool(max(multiprocessing.cpu_count() - 2, 1)) as pool:
        data = list(tqdm(pool.imap(get_vxtweet, df.url), total=df.url.shape[0]))
        df = pd.concat([df, data])
    df.to_csv(SAVE_DIR)
    alert(f"All data has been saved to '{SAVE_DIR}'")