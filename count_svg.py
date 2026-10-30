"""Count CC HTML responses with an inline <svg> start tag (stdlib HTMLParser, so <script> text is skipped)."""
import json, re, sys
from html.parser import HTMLParser
from multiprocessing import Pool
from cc import html_responses


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.svg = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'svg':
            self.svg += 1


def check(args):
    url, text = args
    if not re.search(r'<svg[\s>/]', text, re.I):
        return url, 0
    p = P()
    try:
        p.feed(text)
    except Exception:
        return url, -1
    return url, p.svg


if __name__ == '__main__':
    out = open(sys.argv[2], 'w')
    total = hits = 0
    with Pool(8) as pool:
        for url, n in pool.imap_unordered(check, html_responses(sys.argv[1]), chunksize=50):
            total += 1
            if n > 0:
                hits += 1
                out.write(json.dumps({'url': url.split('?')[0], 'svg': n}) + '\n')
    print(json.dumps({'warc': sys.argv[1].rsplit('/', 1)[-1], 'html_responses': total,
                      'with_inline_svg': hits, 'pct': round(100 * hits / total, 2)}))
