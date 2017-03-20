#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import hashlib
import traceback
import itertools

# For Py 3

import time

# OPTIONS
sleep_delay = 3
# END OPTIONS

text_type = str

known_mimetypes = {'image/svg+xml': '.svg',
                   'image/png': '.png',
                   'image/tiff': '.tif',
                   'image/jpeg': '.jpg',
                   'image/jpg': '.jpg',
                   'image/pjpeg': '.jpg',
                   'image/gif': '.gif',
                   'image/bmp': '.bmp', # it's disabled in Sigil
                   'image/x-ms-bmp': '.bmp',
                   'application/octet-stream': 'NONE',
                   # 'image/x-windows-bmp': '.bmp',
                   }

list_known_img_ext = tuple(known_mimetypes.values())

try:
    from lxml import html as LxmlHtml


    def get_urls_from_page(html_data):
        assert (isinstance(html_data, str), 'html must be an str!')
        global list_known_img_ext
        lxml_doc = LxmlHtml.fromstring(html_data.encode('utf-8'))
        return itertools.chain(filter(lambda url: url.startswith('../Images/'), lxml_doc.xpath('//img/@src')),
                                   filter(lambda url: url.startswith('../Images/') and url.lower().endswith(list_known_img_ext),
                                   lxml_doc.xpath('//a/@href'))
                                   )

except ImportError:
    from html.parser import HTMLParser


    class MyParse(HTMLParser):
        def __init__(self, known_img_ext):
            assert(isinstance(known_img_ext, (list, tuple)), 'known_img_ext parameter must be list or tuple!')
            super().__init__()
            self._img_urls = []
            self._list_known_img_ext = known_img_ext

        def handle_starttag(self, tag, attrs):
            if tag == "img":
                _url = dict(attrs)["src"]
                if _url.startswith('../Images/'):
                    self._img_urls.append(_url)
            elif tag == 'a':
                _url = dict(attrs)["href"]
                if _url.startswith('../Images/') and _url.lower().endswith(self._list_known_img_ext):
                    self._img_urls.append(_url)

        def get_img_urls(self):
            return self._img_urls


    def get_urls_from_page(html_data):
        assert (isinstance(html_data, str), 'html must be an str!')
        parser = MyParse(list_known_img_ext)
        parser.feed(html_data)
        return parser.get_img_urls()


def run(bk):
    """
    Plugin entry point
    :param bk: instance of class BookContainer from Sigil API
    :return: success code
    """
    # See https://github.com/Sigil-Ebook/Sigil/blob/master/src/Resource_Files/plugin_launchers/python/bookcontainer.py#L230
    exists_image_tupl = [(_id, _href) for _id, _href, _mime in bk.image_iter()]
    exists_image_href_set = set(x[1] for x in exists_image_tupl)
    used_image_href_set = set()

    # For all xhtml files, _id - is a base filename, href - path
    for (_id, href) in bk.text_iter():
        print('Chapter found {}:'.format(href))
        # Read xhtml file from book
        html = None
        try:
            html = bk.readfile(_id)
        except Exception as e:
            print(e)
            print("Invalid MANIFEST!")
            print("You may fix content.opf file from you Epub: remove or rename record for:\n%s" % href)
            continue
        if not isinstance(html, text_type):
            html = text_type(html, 'utf-8')

        for url in get_urls_from_page(html):
            url = url.replace('../', '', 1)
            used_image_href_set.add(url)

    difference = exists_image_href_set - used_image_href_set
    for _id, _href in filter(lambda x: x[1] in difference, exists_image_tupl):
        print('Remove unused image: {}'.format(_href))
        bk.deletefile(_id)

    print("FINISHED SUCCESSFUL!")
    return 0


def main():
    print("I reached main when I should not have\n")
    return -1


if __name__ == "__main__":
    sys.exit(main())
