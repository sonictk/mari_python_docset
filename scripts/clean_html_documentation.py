#!/usr/bin/env python
"""
This module is a script that cleans up the default HTML Maya Doxygen
documentation to be usable as standalone.
"""
import sys
import argparse
import logging
import multiprocessing
import os
import shutil
from bs4 import BeautifulSoup
from lib import chunk

DEFAULT_INPUT_DIR_NAME = 'pydoc'
CHUNK_SIZE = 50


def format_file(all_files, docs_path, output_path):
    """
    This function formats the ``list`` of HTML documentation files given and
    writes the output files to a subdirectory.
    """
    logger = logging.getLogger(__name__)
    for i, f in enumerate(all_files):
        if os.path.splitext(f)[-1] != '.html':
            # NOTE: (yliangsiew) For non-HTML files, just copy over
            shutil.copyfile(os.path.join(docs_path, f), os.path.join(output_path, f))
            continue

        html = open(os.path.join(docs_path, f)).read()
        soup = BeautifulSoup(html, 'html.parser')

        # NOTE: (yliangsiew) Remove the top UI navbar
        for t in soup.find_all('table', attrs={'class' : 'navbar'}):
            t.decompose()

        # NOTE: (yliangsiew) Remove the footer
        for td in soup.find_all('td', attrs={'class' : 'footer'}):
            td.decompose()

        # # Also insert anchors in order for table of contents to work
        # for a in soup.find_all('a'):
        #     if a.get('name'):
        #         member_name = td.contents[-1]
        #         if member_name and len(member_name) > 2:
        #             member_name = member_name.split(' ')[-2]
        #             new_tag = soup.new_tag('a')
        #             new_tag['name'] = '//apple_ref/cpp/Function/{0}'.format(member_name)
        #             new_tag['class'] = 'dashAnchor'
        #             td.insert(0, new_tag)

        with open(os.path.join(output_path, f), 'w') as of:
            of.write(str(soup.prettify(formatter='html')))

    logger.debug('Job complete!')


def main(mari_version='401', input_location=''):
    """This is the main entry point of the program."""

    logger = logging.getLogger(__name__)

    output_path = os.path.join(os.path.dirname(
                            os.path.dirname(os.path.abspath(__file__))
                        ),
                          'mari-{0}-python-api.docset'.format(mari_version),
                          'Contents',
                          'Resources',
                          'Documents')

    logger.debug('Using source documentation from: {0}'.format(input_location))
    logger.info('Formatting documentation to directory: {0}'.format(output_path))

    if os.path.isdir(output_path):
        logger.info('Cleaning out existing directory...')
        shutil.rmtree(output_path)
    os.makedirs(output_path)

    all_files = os.listdir(input_location)
    logger.debug('Total number of files to process: {0}'.format(len(all_files)))
    jobs = []
    for s in chunk(all_files, CHUNK_SIZE):
        job = multiprocessing.Process(target=format_file, args=(s, input_location, output_path))
        jobs.append(job)

    logger.debug('Num. of jobs scheduled: {0}'.format(len(jobs)))
    [j.start() for j in jobs]
    logger.info('Jobs submitted, please wait for them to complete!')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print sys.path[0]

    parser = argparse.ArgumentParser(description='This program formats the HTML documentation so that it is usable in the docset.')
    parser.add_argument('-mv',
                        '--mariVersion',
                        default='401',
                        help='The Mari version to generate the docset for.')
    parser.add_argument('-i',
                        '--input',
                        default=os.path.join(os.path.dirname(sys.path[0]), DEFAULT_INPUT_DIR_NAME),
                        help='The location to the original source documentation to format.')
    args = parser.parse_args()

    if not os.path.isdir(args.input):
        raise IOError('The directory: {0} does not exist!'.format(args.input))

    main(mari_version=args.mariVersion, input_location=args.input)
