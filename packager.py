#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zipfile
import os
import sys
import xml.sax


class Stack(object):
    """LIFO stack"""

    def __init__(self):
        self._items = []

    def is_empty(self):
        return len(self._items) == 0

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()

    def pop_or_none(self):
        if self.is_empty():
            return None
        return self.pop()

    def peek(self):
        return self._items[len(self._items)-1]

    def peek_or_none(self):
        if self.is_empty():
            return None
        return self.peek()

    def size(self):
        return len(self._items)

    def __str__(self):
        return '.'.join(self._items)


class PluginInfoHandler(xml.sax.ContentHandler):
    def __init__(self):
        super().__init__()
        self._stack = Stack()
        self.plugin_name = ''
        self.plugin_version = ''

    def startElement(self, name, attrs):
        self._stack.push(name)

    def characters(self, content):
        _current_element = self._stack.peek()
        if _current_element == 'name':
            self.plugin_name = content
        elif _current_element == 'version':
            self.plugin_version = content

    def endElement(self, name):
        self._stack.pop()


def create_zip_fname(handler):
    assert (isinstance(handler, PluginInfoHandler), 'unique_id must be an str!')
    return '{}_v{}.zip'.format(handler.plugin_name, handler.plugin_version)


def process_plugin_folder(path, output_path):
    join = os.path.join
    relpath = os.path.relpath
    # Extract info about plugin
    plugin_xml_fname = join(path, 'plugin.xml')
    if not os.path.exists(plugin_xml_fname):
        print('Invalid plugin folder! File doesn\'t exists: {}'.format(plugin_xml_fname))
        return 1
    handler = PluginInfoHandler()
    xml.sax.parse(plugin_xml_fname, handler)
    plugin_name = handler.plugin_name
    # Create ZIP
    zip_fname = create_zip_fname(handler)
    zip_path = join(output_path, zip_fname)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, False) as myzip:
        for root, dirs, files in os.walk(path):
            if '.idea' in root or '.git' in root:
               continue
            for file in filter(lambda x: not x == 'packager.py' and not x.startswith('.'),
                               files):
                _path = join(root, file)
                # For subfolder with plugin name in ZIP
                _inner_path = join(plugin_name, relpath(_path, path))
                myzip.write(_path, _inner_path)
    return 0

def print_help():
    print('Call {} plugin_folder [output folder]\nOne or two params.'.format(sys.argv[0]))

def main():
    argv = sys.argv[1:]
    if len(argv) > 1:
        p1 = argv[0]
        p2 = argv[1]
        if os.path.exists(p1) and os.path.isdir(p1) and \
           os.path.exists(p2) and os.path.isdir(p2):
            return process_plugin_folder(p1, p2)
        print('One or more arguments not dir (folder) or not exists!')
        print_help()
        return 1
    elif len(argv) == 1:
        p1 = argv[0]
        if p1 in ('--help', '-h', 'help'):
            print_help()
            return 0
        if os.path.exists(p1) and os.path.isdir(p1):
            return process_plugin_folder(p1, p1)
        print_help()
        return 1
    else:
        return process_plugin_folder(os.getcwd(), 'B://')
    return 0


if __name__ == '__main__':
    sys.exit(main())
