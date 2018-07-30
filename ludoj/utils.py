# -*- coding: utf-8 -*-

''' util functions '''

import json
import logging
import os
import string as string_lib

from collections import OrderedDict
from datetime import datetime, timezone
from itertools import groupby
from types import GeneratorType
from urllib.parse import parse_qs, urlparse, urlunparse

import dateutil.parser

LOGGER = logging.getLogger(__name__)

NON_PRINTABLE_SET = frozenset(chr(i) for i in range(128)).difference(string_lib.printable)
NON_PRINTABLE_TANSLATE = {ord(character): None for character in NON_PRINTABLE_SET}


def to_str(string):
    ''' safely returns either string or None '''

    string = (
        string if isinstance(string, str)
        else string.decode() if isinstance(string, bytes)
        else None)
    return string.translate(NON_PRINTABLE_TANSLATE) if string is not None else None


def identity(obj):
    ''' do nothing '''

    return obj


# pylint: disable=unused-argument
def const_true(*args, **kwargs):
    ''' returns True '''

    return True


def normalize_space(item, preserve_newline=False):
    ''' normalize space in a string '''

    item = to_str(item)

    if not item:
        return ''

    if preserve_newline:
        try:
            return '\n'.join(normalize_space(line) for line in item.splitlines()).strip()
        except Exception:
            return ''

    try:
        return ' '.join(item.split())
    except Exception:
        return ''


def clear_list(items):
    ''' return unique items in order of first ocurrence '''

    return list(OrderedDict.fromkeys(filter(None, items)))


def parse_int(string, base=10):
    ''' safely convert an object to int if possible, else return None '''

    if isinstance(string, int):
        return string

    try:
        return int(string, base=base)

    except Exception:
        pass


    try:
        return int(string)

    except Exception:
        pass

    return None


def parse_float(number):
    ''' safely convert an object to float if possible, else return None '''

    try:
        return float(number)
    except Exception:
        pass

    return None


def batchify(iterable, size, skip=None):
    ''' yields batches of the given size '''

    iterable = (x for x in iterable if x not in skip) if skip is not None else iterable
    for _, group in groupby(enumerate(iterable), key=lambda x: x[0] // size):
        yield (x[1] for x in group)


def extract_query_param(url, field):
    ''' extract a specific field from URL query parameters '''

    url = urlparse(url)
    query = parse_qs(url.query)
    values = query.get(field)

    return values[0] if values else None


def now(tzinfo=None):
    ''' current time in UTC or given timezone '''

    result = datetime.utcnow().replace(microsecond=0, tzinfo=timezone.utc)
    return result if tzinfo is None else result.astimezone(tzinfo)


def _add_tz(date, tzinfo=None):
    return date if not tzinfo or not date or date.tzinfo else date.replace(tzinfo=tzinfo)


def parse_date(date, tzinfo=None, format_str=None):
    '''try to turn input into a datetime object'''

    if not date:
        return None

    # already a datetime
    if isinstance(date, datetime):
        return _add_tz(date, tzinfo)

    # parse as epoch time
    timestamp = parse_float(date)
    if timestamp is not None:
        return datetime.fromtimestamp(timestamp, tzinfo or timezone.utc)

    if format_str:
        try:
            # parse as string in given format
            return _add_tz(datetime.strptime(date, format_str), tzinfo)
        except Exception:
            pass

    try:
        # parse as string
        return _add_tz(dateutil.parser.parse(date), tzinfo)
    except Exception:
        pass

    try:
        # parse as (year, month, day, hour, minute, second, microsecond, tzinfo)
        return datetime(*date)
    except Exception:
        pass

    try:
        # parse as time.struct_time
        return datetime(*date[:6], tzinfo=tzinfo or timezone.utc)
    except Exception:
        pass

    return None


def serialize_date(date, tzinfo=None):
    '''seralize a date into ISO format if possible'''

    parsed = parse_date(date, tzinfo)
    return parsed.strftime('%Y-%m-%dT%T%z') if parsed else str(date) if date else None


def _json_default(obj):
    if isinstance(obj, (set, frozenset, range, GeneratorType)) or hasattr(obj, '__iter__'):
        return list(obj)
    if isinstance(obj, datetime):
        return serialize_date(obj)
    return repr(obj)


def serialize_json(obj, file=None, **kwargs):
    '''
    safely serialze JSON, turning iterables into lists, dates into ISO strings,
    and everything else into their representation
    '''

    kwargs.setdefault('default', _json_default)

    if isinstance(file, (str, bytes)):
        LOGGER.info('opening file <%s> and writing JSON content', file)

        path_dir = os.path.abspath(os.path.split(file)[0])
        os.makedirs(path_dir, exist_ok=True)

        with open(file, 'w') as json_file:
            return json.dump(obj, json_file, **kwargs)

    if file is not None:
        LOGGER.info('writing JSON content to opened file pointer <%s>', file)
        return json.dump(obj, file, **kwargs)

    return json.dumps(obj, **kwargs)


def smart_walk(path, raise_exc=False, accept_path=const_true, **s3_args):
    ''' walk a directory '''

    url = urlparse(to_str(path)) if isinstance(path, (bytes, str)) else path
    path = url.path if url.path.endswith(os.path.sep) else url.path + os.path.sep

    if url.scheme == 's3':
        try:
            import boto
            from smart_open import s3_iter_bucket
        except ImportError as exc:
            LOGGER.error('<boto> and <smart_open> libraries must be importable')
            LOGGER.exception(exc)
            if raise_exc:
                raise exc
            else:
                return

        path = path[1:]
        # regex = re.compile('^{}'.format(re.escape(path)))

        try:
            bucket = boto.connect_s3().get_bucket(url.hostname)
            for key, content in s3_iter_bucket(
                    bucket, prefix=path, accept_key=accept_path, **s3_args):
                yield urlunparse(('s3', bucket.name, key.key, None, None, None)), content

        except Exception as exc:
            LOGGER.exception(exc)
            if raise_exc:
                raise exc

        return

    path = os.path.abspath(path)

    for sub_dir, _, file_paths in os.walk(path):
        for file_path in file_paths:
            file_path = os.path.join(sub_dir, file_path)

            if not accept_path(file_path):
                continue

            try:
                with open(file_path, 'rb') as file_obj:
                    yield urlunparse(('file', None, file_path, None, None, None)), file_obj.read()

            except Exception as exc:
                LOGGER.exception(exc)
                if raise_exc:
                    raise exc


def smart_walks(*paths, raise_exc=False, **kwargs):
    ''' walk all paths '''

    for path in paths:
        url = urlparse(to_str(path)) if isinstance(path, (bytes, str)) else path

        if url.path.endswith('/'):
            yield from smart_walk(url, raise_exc=raise_exc, **kwargs)
            continue

        if url.scheme == 's3':
            try:
                from smart_open import smart_open
                with smart_open(url.geturl(), 'rb') as file_obj:
                    yield url.geturl(), file_obj.read()
                continue

            except Exception:
                pass

            yield from smart_walk(url, raise_exc=raise_exc, **kwargs)

            continue

        path = os.path.abspath(url.path)

        if os.path.isdir(path):
            yield from smart_walk(path, raise_exc=raise_exc, **kwargs)
            continue

        try:
            with open(path, 'rb') as file_obj:
                yield urlunparse(('file', None, path, None, None, None)), file_obj.read()

        except Exception as exc:
            LOGGER.exception(exc)
            if raise_exc:
                raise exc
