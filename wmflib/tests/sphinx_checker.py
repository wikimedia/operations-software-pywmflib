"""Sphinx configuration checker.

- Check that all the existing wmflib modules are listed in the API index documentation.
- Check that all the modules listed in the API index documentation exists in wmflib.
- Check that all the listed modules have its own file in the api/ documentation directory.
  Sphinx would raise a warning but not fail in this case.
"""
import argparse
import os
import pkgutil
import sys

import wmflib


DOC_API_BASE_PATH = 'doc/source/api'
DOC_API_INDEX_PATH = os.path.join(DOC_API_BASE_PATH, 'index.rst')
API_INDEX_PREFIX = '    wmflib.'
EXCLUDED_NAMES = ()


def main(base_path):
    """Perform the check."""
    wmflib_modules = {name for _, name, ispkg in pkgutil.iter_modules(wmflib.__path__)
                      if not ispkg and name not in EXCLUDED_NAMES}

    doc_path = os.path.join(base_path, DOC_API_INDEX_PATH)
    with open(doc_path) as f:
        api_index_lines = f.readlines()

    doc_api_lines = [line.strip() for line in api_index_lines if line.startswith(API_INDEX_PREFIX)]
    doc_api_modules = {line.split('.', 1)[1] for line in doc_api_lines}

    ret = 0
    if wmflib_modules - doc_api_modules:
        print('wmflib modules that are not listed in {doc}: {modules}'.format(
            doc=DOC_API_INDEX_PATH, modules=wmflib_modules - doc_api_modules))
        ret += 1
    if doc_api_modules - wmflib_modules:
        print('Documented modules in {doc} that are missing in wmflib: {modules}'.format(
            doc=DOC_API_INDEX_PATH, modules=doc_api_modules - wmflib_modules))
        ret += 1

    doc_api_files = ['wmflib.{name}.rst'.format(name=name) for name in doc_api_modules]
    missing_doc_api_files = [file for file in doc_api_files
                             if not os.path.isfile(os.path.join(DOC_API_BASE_PATH, file))]
    if missing_doc_api_files:
        print('Missing documentation files in {doc}: {files}'.format(
            doc=DOC_API_BASE_PATH, files=missing_doc_api_files))
        ret += 1

    if ret == 0:
        print('All wmflib modules are documented')

    return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser(  # pylint: disable=invalid-name
        description='Check that all wmflib modules are documented')
    parser.add_argument('base_path', help='Path to the root of the wmflib repository')
    args = parser.parse_args()  # pylint: disable=invalid-name

    sys.exit(main(args.base_path))
