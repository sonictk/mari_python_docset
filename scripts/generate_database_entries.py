#!/usr/bin/env python
"""
This module is a command-line utility that writes to the SQLite database that
is used for lookup of documentation entries.
"""
import argparse
import logging
import multiprocessing
import os
import sqlite3
import time
from bs4 import BeautifulSoup
from lib import chunk

DEFAULT_MARI_VERSION='401'


def clean_database(database_file_path):
    """This clears the database of current search entries."""
    logger = logging.getLogger(__name__)
    logger.debug('Making connection to database...')
    conn = sqlite3.connect(database_file_path)
    cur = conn.cursor()

    try:
        logger.debug('Cleaning database...')
        cur.execute('DROP TABLE searchIndex;')
    except:
        raise RuntimeError('Failed to clear out database! Aborting operation!')
    finally:
        cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
        cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')


def write_entry_for_class(cur, class_name, path, docs_root, maya_version):
    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path)'
            ' VALUES (\'{name}\', \'Class\', \'{path}\')'.format(name=class_name, path=path))

    # Now start finding items within the class pages to add
    # additional entries for
    html = open(os.path.join(docs_root, path)).read()
    soup = BeautifulSoup(html, 'html.parser')

    # for h2 in soup.find_all('h2', {'class': 'groupheader'}):
    #     # Now find all public types defined in the class and create
    #     # links to them
    #     if h2.a and h2.a.get('name') == 'pub-types':
    #         items = h2.parent.parent.parent.find_all(
    #             'td',
    #             {'class' : 'memItemRight'}
    #         )
    #         # Do not consider inherited types
    #         for pub_type_item in items:
    #             if 'el' not in pub_type_item.a.get('class'):
    #                 continue
    #             if 'inherit' in pub_type_item.parent.get('class'):
    #                 continue
    #             type_name = pub_type_item.a.string
    #             type_url = pub_type_item.a.get('href')

    #             # NOTE: For Maya 2017, it seems the URL is
    #             # formatted differently
    #             if maya_version == '2017':
    #                 type_url = type_url.replace('#!/url=./cpp_ref/', '')
    #             if type_name and type_url:
    #                 cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path)'
    #                         ' VALUES (\'{class_name}::{type_name}\', \'Type\', \'{path}\')'
    #                         .format(class_name=class_name, type_name=type_name, path=type_url))
    #     elif h2.a and h2.a.get('name') == 'pub-methods':
    #         pub_methods = h2.parent.parent.parent.find_all(
    #             'td',
    #             {'class' : 'memItemRight'}
    #         )
    #         # Do not consider inherited functions
    #         for m in pub_methods:
    #             if 'el' not in m.a.get('class'):
    #                 continue
    #             if 'inherit' in m.parent.get('class'):
    #                 continue
    #             method_name = m.a.string
    #             method_url = m.a.get('href')
    #             # NOTE: For Maya 2017, it seems the URL is
    #             # formatted differently
    #             if maya_version == '2017':
    #                 method_url = method_url.replace('#!/url=./cpp_ref/', '')
    #             if method_name and method_url:
    #                 cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path)'
    #                         ' VALUES (\'{class_name}::{method_name}\', \'Method\', \'{path}\')'
    #                         .format(class_name=class_name,
    #                                 method_name=method_name,
    #                                 path=method_url))
    #     elif h2.a and h2.a.get('name') == 'pub-static-methods':
    #         pub_methods = h2.parent.parent.parent.find_all(
    #             'td',
    #             {'class' : 'memItemRight'}
    #         )
    #         # Do not consider inherited functions
    #         for m in pub_methods:
    #             if 'el' not in m.a.get('class'):
    #                 continue
    #             if 'inherit' in m.parent.get('class'):
    #                 continue
    #             method_name = m.a.string
    #             method_url = m.a.get('href')
    #             # NOTE: For Maya 2017, it seems the URL is
    #             # formatted differently
    #             if maya_version == '2017':
    #                 method_url = method_url.replace('#!/url=./cpp_ref/', '')
    #             if method_name and method_url:
    #                 cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path)'
    #                         ' VALUES (\'{class_name}::{method_name}\', \'Function\', \'{path}\')'
    #                         .format(class_name=class_name,
    #                                 method_name=method_name,
    #                                 path=method_url))
    #     elif h2.a and h2.a.get('name') == 'pro-methods':
    #         pub_methods = h2.parent.parent.parent.find_all(
    #             'td',
    #             {'class' : 'memItemRight'}
    #         )
    #         # Do not consider inherited functions
    #         for m in pub_methods:
    #             if 'el' not in m.a.get('class'):
    #                 continue
    #             method_name = m.a.string
    #             method_url = m.a.get('href')
    #             if method_name and method_url:
    #                 cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path)'
    #                         ' VALUES (\'{class_name}::{method_name}\', \'Method\', \'{path}\')'
    #                         .format(class_name=class_name,
    #                                 method_name=method_name,
    #                                 path=method_url))


def write_entries(database_file_path,
                  filenames,
                  docs_root,
                  mari_version=DEFAULT_MARI_VERSION,
                  timeout=120.0):
    """This function writes search entries to the database."""

    logger = logging.getLogger(__name__)

    conn = sqlite3.connect(database_file_path, timeout=timeout)
    cur = conn.cursor()

    for f in filenames:
        if not os.path.splitext(f)[-1] == '.html' or not f.startswith('mari.'):
            continue

        if f.endswith('-class.html'):
            # NOTE: (yliangsiew) This handles normal class files like ``mari.GeoEntity.ChannelDestroyStrategy-class.html``
            class_name = '{0}'.format(f.split('mari.')[-1].split('-class')[0])
            # NOTE: (yliangsiew) This handles files like ``mari.utils.node_generator.Node-class.html``
            if '.' in class_name:
                class_name = class_name.split('.')[-1]
            write_entry_for_class(cur, class_name, f, docs_root, mari_version)

        elif f.startswith('mari.examples.'):
            example_name = f[len('mari.examples.'):-len('.html')]
            cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path)'
                        ' VALUES (\'{name}\', \'Sample\', \'{path}\')'.format(name=example_name, path=f))

    try: conn.commit()
    except sqlite3.OperationalError:
        logger.warning('Encountered database lock, attemping again after 5 seconds...')
        time.sleep(5)
        conn.commit()
    finally:
        logger.debug('Job {0} complete, closing connection to database...'.format(os.getpid()))
        conn.close()


def main(mari_version=DEFAULT_MARI_VERSION):
    """This is the main entry point of the program."""

    logger = logging.getLogger(__name__)

    database_file_path = os.path.join(os.path.dirname(
                            os.path.dirname(os.path.abspath(__file__))
                        ),
                                      'mari-{0}-python-api.docset'.format(mari_version),
                                      'Contents',
                                      'Resources',
                                      'docSet.dsidx')
    if not os.path.isfile(database_file_path):
        raise IOError('The database file: {0} does not exist!'
                .format(database_file_path))

    # Clean the database of existing entries
    clean_database(database_file_path)

    # Write entries
    docs_root = os.path.join(os.path.dirname(database_file_path), 'Documents')

    if not os.path.isdir(docs_root):
        os.makedirs(docs_root)

    logger.debug('Inserting entries into database...')
    all_files = os.listdir(docs_root)
    logger.debug('Total number of files to process: {0}'.format(len(all_files)))

    jobs = []
    for s in chunk(all_files, 250):
        job = multiprocessing.Process(target=write_entries,
                args=(database_file_path, s, docs_root, mari_version))
        jobs.append(job)

    logger.debug('Num. of jobs scheduled: {0}'.format(len(jobs)))
    [j.start() for j in jobs]
    logger.info('Jobs submitted, please wait for them to complete!')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='This program generates the database entries for the docset.program')
    parser.add_argument('-mv',
                        '--mariVersion',
                        default=DEFAULT_MARI_VERSION,
                        help='The Mari version to generate the docset for.')
    args = parser.parse_args()
    main(args.mariVersion)
