"""Sphinx configuration checker.

- Check that all the existing wmflib modules are listed in the API index documentation.
- Check that all the modules listed in the API index documentation exists in wmflib.
- Check that all the listed modules have its own file in the api/ documentation directory.
  Sphinx would raise a warning but not fail in this case.
"""
import argparse
import pkgutil
import sys

from pathlib import Path

import wmflib


DOC_API_BASE_PATH = Path('doc/source/api')
DOC_API_INDEX_PATH = DOC_API_BASE_PATH / 'index.rst'
API_INDEX_PREFIX = '    wmflib.'
EXCLUDED_NAMES = ()


def main(base_path):
    """Perform the check."""
    wmflib_modules = {name for _, name, ispkg in pkgutil.iter_modules(wmflib.__path__)
                      if not ispkg and name not in EXCLUDED_NAMES}

    doc_path = base_path / DOC_API_INDEX_PATH
    with open(doc_path, encoding='utf-8') as f:
        api_index_lines = f.readlines()

    doc_api_lines = [line.strip() for line in api_index_lines if line.startswith(API_INDEX_PREFIX)]
    doc_api_modules = {line.split('.', 1)[1] for line in doc_api_lines}

    ret = 0
    if wmflib_modules - doc_api_modules:
        print(f'wmflib modules that are not listed in {DOC_API_INDEX_PATH}: {wmflib_modules - doc_api_modules}')
        ret += 1
    if doc_api_modules - wmflib_modules:
        print(f'Documented modules in {DOC_API_INDEX_PATH} that are missing in wmflib: '
              f'{doc_api_modules - wmflib_modules}')
        ret += 1

    doc_api_files = [f'wmflib.{name}.rst' for name in doc_api_modules]
    missing_doc_api_files = [file for file in doc_api_files
                             if not (DOC_API_BASE_PATH / file).is_file]
    if missing_doc_api_files:
        print(f'Missing documentation files in {DOC_API_BASE_PATH}: {missing_doc_api_files}')
        ret += 1

    if ret == 0:
        print('All wmflib modules are documented')

    return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Check that all wmflib modules are documented')
    parser.add_argument('base_path', help='Path to the root of the wmflib repository')
    args = parser.parse_args()

    sys.exit(main(args.base_path))
