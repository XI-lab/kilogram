import re
from ...lang.tokenize import wiki_tokenize_func


ENTITY_MATCH_RE = re.compile(r'<(.+)\|(.+)>')
SIMPLE_TYPES = set(['Place', 'Person', 'Organisation'])


def parse_types_text(text, dbpedia_types, type_level=-1, type_filter=None):
    """
    :type dbpedia_types: dict
    """
    new_line = []
    new_line_plain = []
    for word in text.split():
        res = None
        res1 = None
        match = ENTITY_MATCH_RE.search(word)
        if match:
            uri = match.group(1)
            orig_text = match.group(2)
            orig_text = orig_text.replace('_', ' ')
            for uri in (uri, uri.capitalize()):
                if uri in dbpedia_types:
                    types = dbpedia_types[uri]
                    dbp_type = types[type_level]
                    if type_filter and dbp_type not in type_filter:
                        continue
                    res = [('<dbpedia:' + dbp_type+'>', 1)]
                    res1 = wiki_tokenize_func(orig_text)
                    break
            if not res:
                res = wiki_tokenize_func(orig_text)
        else:
            res = [word]
        new_line.extend(res)
        if res1:
            res = res1
        new_line_plain.extend(res)
    return new_line, new_line_plain
