# coding=utf-8
from __future__ import unicode_literals
import json
from itertools import tee, islice, izip_longest

import fuzzy
import re
import pytesser


def peek(some_iterable, window=1):
    items, nexts = tee(some_iterable, 2)
    nexts = islice(nexts, window, None)
    return izip_longest(items, nexts)


def run(filename, debug=False):
    content = pytesser.image_file_to_string(filename)

    def find_match(text, pattern, minimum=0.7):
        score, match, start, end = fuzzy.bitap(text, pattern)

        if not match or score <= minimum:
            return None, None, None, None

        return score, match, start, end

    content = unicode(content, 'utf-8')

    _, alarm, _, end = find_match(content, 'ALARMDEPESCHE')

    keys = json.loads(file('ocr/keywords.json').read())
    keys = sorted(keys, key=lambda k: len(k['name']), reverse=True)

    if alarm is not None:
        content = content[end:]

        _, engines, start, _ = find_match(content, 'Einsatzmittelliste')
        content = content[:start]

        if debug:
            print content

        original = content

        for key in keys:
            name = key['name']
            score, match, start, end = find_match(content, name)

            if match:
                skip = False
                for exclude in key.get('exclude', []):
                    alt, _, _, _ = find_match(match, exclude) # should honor the threshold of the exclude
                    if alt > score:
                        skip = True

                if skip:
                    continue

                newline = content[:start].rfind('\n')

                if newline == -1 or (start - newline) <= 10:
                    key['score'] = score
                    key['match'] = match
                    key['start'] = start
                    key['end'] = end

                    content = content[:start] + re.sub(r'[^\n]', ' ', match) + content[end:]

        matched = filter(lambda k: k.get('match') is not None, keys)
        tokens = sorted(matched, key=lambda k: k['start'])

        for token, next_token in peek(tokens):
            end = len(original) if next_token is None else next_token['start']
            token['content'] = re.sub(r'^[ .:‘]+', '', original[token['end']:end].strip()).strip()

        tokens = filter(lambda k: not k.get('ignore', False), tokens)

        if debug:
            import pprint

            pprint.PrettyPrinter(indent=4).pprint(tokens)

        return {token['name']: token['content'] for token in tokens}

    return []