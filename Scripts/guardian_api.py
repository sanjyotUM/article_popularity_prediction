#!/usr/bin/env python
# coding: utf-8

import time
import sys
import csv
from concurrent.futures import ThreadPoolExecutor as PoolExecutor

import pandas as pd

from theguardian import theguardian_content


apikey = 'bcbe869c-83c9-4084-b72e-bd2af0e6f6ae'


def append_to_headlines(articleid, section_name, publish_date, title, fileobj):
    w = csv.writer(fileobj, delimiter='|')
    try:
        w.writerow([articleid, section_name, publish_date, title])
    except Exception as e:
        print('Exception: {}'.format(e))
    return


def write_headlines(dfid):
    url = 'https://content.guardianapis.com/{}'.format(dfid)

    content = theguardian_content.Content(api=apikey, url=url)
    raw_content = content.get_request_response()

    day_count = int(raw_content.headers['X-RateLimit-Remaining-day'])
    minute_count = int(raw_content.headers['X-RateLimit-Remaining-minute'])

    if day_count < 50:
        print('API call daily limit reached. Exiting')
        try:
            sys.exit()
        except:
            exit
    elif minute_count < 20:
        print('Pausing to avoid crossing minute limit')
        time.sleep(70)
    elif raw_content.status_code == 200:
        j = raw_content.json()
        try:
            articleid = j['response']['content']['id']
            section_name = j['response']['content']['sectionName']
            publish_date = j['response']['content']['webPublicationDate']
            title = j['response']['content']['webTitle']
            append_to_headlines(articleid, section_name, publish_date, title, f)
        except Exception as e:
            print('Exception: {}'.format(e))
            print('Happened at: {}'.format(url))
    else:
        pass
        # print('Detected status code: {}'.format(raw_content.status_code))
        # print('For request: {}'.format(url))


if __name__ == '__main__':
    features_path = '../Datasets/Headlines/guardian_main_model/guardian_test.csv'
    labels_path = '../Datasets/Headlines/guardian_popularity_measures/guardian_train_popularity.csv'
    headline_path = '../Datasets/Headlines/guardian_headlines/headlines_test.csv'

    guar = pd.read_csv(features_path)
    # popularity = pd.read_csv(labels_path)

    articles = guar['article_id'].tolist()

    with open(headline_path, 'a') as f:
        with PoolExecutor(max_workers=10) as executor:
            for i, _ in enumerate(executor.map(write_headlines, articles)):
                if i % 100 == 0:
                    print('Headlines done: {}'.format(i))
                pass
