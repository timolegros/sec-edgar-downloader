import os
from pathlib import Path
from sec_edgar_downloader.Downloader import Downloader
# os.remove('D:/Projects/PycharmProjects/sec-edgar-downloader/exampleSEC.txt')

# os.remove(Path.home().joinpath("Downloads", 'test.txt'))

# os.listdir(Path.home().joinpath("Downloads"))

dl = Downloader(s3=True, aws_access_key_id='AKIAZ5MWHWCP5PHNP3G3', aws_secret_access_key='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',
                bucket_name='secfilesfinal', region_name='eu-west-3')
dl.get("10-K", "MSFT")