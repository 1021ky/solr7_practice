from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import XMLParser
from xml.etree.ElementTree import SubElement, ParseError

from collections import defaultdict

class Wikipedia_XMLParser():

    def __init__(self, format, in_file, out_file):
        self._format = format
        self._in_file = in_file
        self._out_file = out_file

    def parse(self, offset, doc_num):
        root = None
        new_root = Element('add')
        counter = 0
        stop = offset + doc_num
        with open(self._in_file, mode='r', encoding='shift-jis', errors='ignore') as f:
            context = ET.iterparse(f, events=('start', 'end'))
            _, root = next(context)  # 一つ進めて root を得る
            new_child = None
            for event, elem in context:
                field = ()
                if event == 'start' and elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}page':
                    counter += 1
                    if counter <= offset:
                        root.clear()
                        continue
                    if counter > stop:
                        break
                    new_child = SubElement(new_root, 'doc')
                elif event == 'end' and elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}title':
                    field = ('title', elem.text)
                elif event == 'end' and elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}timestamp':
                    field = ('timestamp', elem.text)
                elif event == 'end' and elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}contibutor':
                    field = ('contibutor', elem.text)
                elif event == 'end' and elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}username':
                    field = ('username' ,elem.text)
                elif event == 'end' and elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}comment':
                    field = ('comment' ,elem.text)
                elif event == 'end' and elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}text':
                    field = ('text' ,elem.text)
                else:
                    pass
                if new_child != None and field != ():
                    name, text = field
                    e = SubElement(new_child, 'field', attrib={'name': name})
                    e.text = text
                    root.clear()
        filename = str(offset)+self._out_file
        with open(filename, 'w') as f:
            ElementTree(new_root).write(f, encoding="unicode")
            print(f'----------{filename} is written.----------')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="")
    parser.add_argument(
        '-f',
        '--filename',
        help='パース対象のファイル',
        type=str,
        required=True)
    parser.add_argument(
        '-o',
        '--out',
        help="出力先のファイル",
        default="parsed.xml",
        type=str)
    parser.add_argument(
        '-fm',
        '--format',
        type=str,
        default='xml',
        choices=['xml','json'])
    args = parser.parse_args()
    input = args.filename
    output = args.out
    format = args.format

    parser = Wikipedia_XMLParser(format, input, output)
    offset = 0
    doc_num = 30
    while(offset <= 1000000):
        parser.parse(offset=offset, doc_num=doc_num)
        offset += doc_num
