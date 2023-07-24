import os
from typing import Optional

from furl import furl
import ndjson
from urllib3.util import Retry
import requests
from requests.adapters import HTTPAdapter
import throttle

class Crawler:
    fp = None
    writer = None
    last_response = None
    cur_index = 0
    record_count = 0

    session = requests.Session()

    retries = Retry(
        total=5,
        backoff_factor=0.1,
        status_forcelist=[500, 502, 503, 504],
    )

    def __init__(self,
        output_file: str,
        base_url: str,
        index_type: str = 'one',
        page_type: str = 'index',
        page_field: str = 'page',
        result_id_field: str = 'id',
        json_field: Optional[str] = 'posts',
        next_id: str = ''
    ):
        self.output_file = output_file
        self.base_url = base_url
        self.index_type = index_type
        self.page_type = page_type
        self.page_field = page_field
        self.next_id = next_id
        self.result_id_field = result_id_field
        self.json_field = json_field

        self.adapter = HTTPAdapter(max_retries=self.retries)
        self.session.mount('http://', self.adapter)
        self.session.mount('https://', self.adapter)

    def crawl(self):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        self.fp = open(self.output_file, 'w')
        self.writer = ndjson.writer(self.fp)

        result = True

        while result is not None:
            result = self.fetch()

            if result is not None:
                records = result.get(self.json_field, []) if self.json_field is not None else result

                if len(records) == 0:
                    break

                self.last_response = result
                self.save_json(records)
                self.next_id = records[-1][self.result_id_field]
                self.record_count += len(records)

            self.cur_index += 1

        self.fp.close()
        print(f'Crawled {self.cur_index} page(s) and found {self.record_count} record(s)')

    # max 3 requests/s
    @throttle.wrap(1, 3)
    def fetch(self):
        url = self.get_url()

        print(f'[#{self.cur_index + 1}] Fetching {url}')

        r = requests.get(url, headers={
            'user-agent': 'e621-crawler/1.0 (by @hearmeneigh)'
        })

        if r.status_code != 200:
            if r.status_code == 404:
                return None

            raise Exception(f'Failed to crawl {url} with status code {r.status_code}')

        return r.json()

    def get_url(self):
        index = self.cur_index if self.page_type == 'index' else self.next_id

        if self.index_type == 'one':
            index += 1

        url = furl(self.base_url)
        url.add({f'{self.page_field}': str(index)})

        return str(url)

    def save_json(self, records):
        for row in records:
            self.writer.writerow(row)
