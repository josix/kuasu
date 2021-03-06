import re
from urllib.parse import parse_qs, urlparse

from thiamsu.models.hanzi_hanlo_mapping import HanziHanloMapping


def is_valid_youtube_id(youtube_id):
    pattern = r"[A-Za-z0-9\-\_]{11}"
    return True if re.match(pattern, youtube_id) else False


def get_youtube_id_from_url(url):
    # reference
    # https://stackoverflow.com/questions/45579306/get-youtube-video-url-or-youtube-video-id-from-a-string-using-regex
    url_parsed = urlparse(url)

    # validate host
    host = url_parsed.netloc
    if host not in ["youtube.com", "www.youtube.com", "youtu.be"]:
        return

    # get youtube id from url
    query_v = parse_qs(url_parsed.query).get("v")
    youtube_id = None
    if query_v:
        # case1: http://youtube.com/watch?v=iwGFalTRHDA
        youtube_id = query_v[0]
    else:
        # case2: http://youtu.be/t-ZRX8984sc
        paths = url_parsed.path.split("/")
        if paths:
            youtube_id = paths[-1]

    # validate youtube_id
    if youtube_id and is_valid_youtube_id(youtube_id):
        return youtube_id


def translate_hanzi_to_hanlo(hanzi):
    if not hanzi:
        return hanzi

    hanlo = hanzi
    hanzi_hanlo_mapping = HanziHanloMapping.dump()

    for word in sorted(hanzi_hanlo_mapping.keys(), key=lambda k: len(k), reverse=True):
        hanlo = hanlo.replace(word, " %s " % hanzi_hanlo_mapping[word])
    hanlo = re.sub("\s\s+", " ", hanlo)
    hanlo = hanlo.replace(" --", "--")
    return hanlo
