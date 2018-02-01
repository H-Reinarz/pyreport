#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 09:39:48 2018

@author: henning
"""

import markdown
from os import path

def construct_image_link(im_id, image, desc):
    link = '![{}]({} "{}")'.format(im_id, image, desc)
    print(link)
    return link

def parse_image_link(line, only_files=True):
    if line.startswith('!['):
        line = line[:-1]
        im_id, link = line.split(']')
        im_id = im_id[2:]

        file_path, desc = link[1:-1].split(' ')
        if file_path.startswith('http') and only_files:
            return None
        else:
            return (im_id, file_path, desc[1:-1])

    else:
        return None

def adjust_relative_link(new, origin, file):
    print(new, origin, file, end='\n')
    joined = path.join(origin, file)
    normed = path.normpath(joined)

    print(joined, normed, end='\n')
    rel_path = path.relpath(normed, start=new)

    print(rel_path)
    return rel_path



class Markdowner(object):
    '''Class representing a markdown document
    that is put together in an in-code-reporting style.'''

    def __init__(self, name, directory):
        self.paragraphs = []
        self.template = ('<html>\n<body>\n</body>\n</hmtl>', 'body')
        self.replacements = dict()
        self.name = name
        self.directory = directory
        self.extensions=['markdown.extensions.abbr',
                        'markdown.extensions.attr_list',
                        'markdown.extensions.def_list',
                        'markdown.extensions.fenced_code',
                        'markdown.extensions.footnotes',
                        'markdown.extensions.tables',
                        'markdown.extensions.smart_strong',
                        'markdown.extensions.admonition',
                        'markdown.extensions.codehilite',
                        'markdown.extensions.headerid',
                        'markdown.extensions.meta',
                        'markdown.extensions.nl2br',
                        'markdown.extensions.sane_lists',
                        'markdown.extensions.smarty',
                        'markdown.extensions.toc',
                        'markdown.extensions.wikilinks']

    def __call__(self, markdown_block):
        self.paragraphs.append(markdown_block)

    def __str__(self):
        return self.source

    @property
    def source(self):
        return '\n'.join(self.paragraphs)

    def export_source(self):
        filepath = path.join(self.directory, self.name+'.md')
        with open(filepath, 'w') as output:
            output.write(self.source)


    def set_template(self, html, insert_tag):
        if not html.startswith('<html>'):
            with open(html, 'r') as tmplt:
                self.template = (tmplt.read(), insert_tag)
        else:
            self.template = (html, insert_tag)

    def apply_replacements(self):
        repl_tmplt, insert_tag = self.template

        for flag, replacement in self.replacements.items():
            repl_tmplt = repl_tmplt.replace(flag, str(replacement))

        return (repl_tmplt, insert_tag)

    def paste_to_template(self, tmplt, html):
        close_itag = '</'+tmplt[1]+'>'
        split_tmplt = tmplt[0].split(close_itag)

        start = split_tmplt[0]
        end = '\n' + close_itag + split_tmplt[1]

        return start + html + end

    def convert(self):
        return markdown.markdown(self.source, extensions=self.extensions)

    def render(self):
        return self.paste_to_template(self.apply_replacements(), self.convert())


    def render_to_file(self):
        #CODECS
        filepath = path.join(self.directory, self.name+'.html')
        out_file = markdown.codecs.open(filepath, "w",
                          encoding="utf-8",
                          errors="xmlcharrefreplace")

        out_file.write(self.render())

    def embed_md_file(self, filepath, adjust_links=None, framing=''):

        if adjust_links is not None:
            lines = []
            with open(filepath, 'r') as md_file:
                for line in md_file.readlines():
                    parsed = parse_image_link(line)
                    if parsed is not None and parsed[0] in adjust_links:
                        im_id, link_path, desc = parsed
                        new_path = adjust_relative_link(self.directory,
                                                        path.dirname(filepath),
                                                        link_path)

                        lines.append(construct_image_link(im_id, new_path, desc))

                    else:
                        lines.append(line)

            foreign = '\n'.join(lines)

        else:
            with open(filepath, 'r') as md_file:
                foreign = md_file.read()


        self('\n'.join(('',framing, foreign, framing)))


    def image(self, desc, image, im_id='image'):
        image_link = construct_image_link(im_id, image, desc)
        return '\n'.join(('', image_link, ''))

    def add_image(self, title, image, im_id='image'):
        self(self.image(title, image, im_id))



