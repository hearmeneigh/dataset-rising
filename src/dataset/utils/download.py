from datetime import timedelta
from typing import Optional

import requests
from requests.adapters import HTTPAdapter, Retry
from call_throttle import throttle

from database.entities.post import PostEntity

global_session = requests.Session()
global_retries = Retry(total=10, backoff_factor=0.1)

global_session.mount('http://', HTTPAdapter(max_retries=global_retries))
global_session.mount('https://', HTTPAdapter(max_retries=global_retries))


@throttle(calls=12, period=timedelta(seconds=1))
def global_fetch(url, agent: str) -> Optional[bytes]:
    r = requests.get(url, headers={
        'user-agent': agent
    }, allow_redirects=True)

    if r.status_code != 200:
        print(f'Could not fetch {url}: {r.status_code}')
        return None

    return r.content


def download_image(post: PostEntity, agent: str):
    return global_fetch(post.image_url, agent)
