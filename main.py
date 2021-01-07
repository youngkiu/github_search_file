#-*- encoding: utf8 -*-

import sys
import requests
import time
import csv
import json
import pandas as pd

def get_num_of_files_with_ext(token, ext, repo):
    # https://stackoverflow.com/a/48192349

    # curl \
    #   -H 'Authorization: token MYTOKEN' \
    #   -i "https://api.github.com/search/code?q=extension:EXT+repo:OWNER/REPO"

    request_url = f'https://api.github.com/search/code?q=extension:{ext}+repo:{repo}'
    request_headers = {
        'Authorization': 'token ' + token
    }
    try:
        response = requests.get(
            url=request_url,
            headers=request_headers
        )
        if response.status_code != 200:
            print(f'[Error] {repo}', response.status_code)
            return response.status_code

        results = response.json()
        # print(json.dumps(results, indent=4))
        return [item['path'] for item in results['items']]
    except Exception as e:
        print('[Error] ', e)
        return None


def get_repositories(token, page_num):
    # https://github.community/t/how-to-get-list-of-private-repositories-via-api-call/120175/3
    # https://stackoverflow.com/a/21909135

    # curl \
    #   -H 'Authorization: token MYTOKEN' \
    #   -H "Accept: application/vnd.github.v3+json" \
    #   https://api.github.com/user/repos

    request_url = f'https://api.github.com/user/repos?page={page_num}'
    request_headers = {
        'Authorization': 'token ' + token
    }
    try:
        response = requests.get(
            url=request_url,
            headers=request_headers
        )
        if response.status_code != 200:
            print(f'[Error] {page_num}', response.status_code)
            return response.status_code

        results = response.json()
        # print(json.dumps(results, indent=4))
        return [repo['full_name'] for repo in results]
    except Exception as e:
        print('[Error] ', e)
        return None


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} [token]')
        sys.exit()

    _token = sys.argv[1]

    _org_name = 'vuno'
    _file_exts = ['sh', 'yml', 'py', 'js']

    _columns = ['repo name', ]
    for _file_ext in _file_exts:
        _columns.append(f'.{_file_ext} files')

    # https://stackoverflow.com/a/24888331/6572046
    df = pd.DataFrame(columns=_columns)

    # https://stackoverflow.com/questions/30656761/github-search-api-only-return-30-results
    _page_num = 1  # github default page_size: 30
    _row_index = 0
    while True:
        _repo_list = get_repositories(_token, _page_num)
        if not _repo_list:
            break

        for _repo in _repo_list:
            if not _repo.startswith(_org_name):
                continue

            _name = _repo[_repo.find('/')+1:]
            _row = [_name, ]

            for _file_ext in _file_exts:
                _path_list = get_num_of_files_with_ext(_token, _file_ext, _repo)
                if isinstance(_path_list, list):
                    print(_name, f'.{_file_ext}', len(_path_list), _path_list)
                else:
                    print(f'[Error] {_org_name}: {_path_list}')
                _row.append(_path_list)
                time.sleep(2)  # Don't delete this code. Without this code, will get a 403 return

            df.loc[_row_index] = _row
            _row_index += 1

        _page_num += 1

    csv_path = f'{_org_name}_repo_file_num.csv'
    with open(csv_path, 'w', encoding='UTF-8') as file:
        csv_writer = csv.writer(file)

        csv_row = []
        for i, col in enumerate(_columns):
            csv_row.append(col)
            if i == 0:
                continue
            csv_row.append(f'# {col}')

        print(csv_row)
        csv_writer.writerow(csv_row)

        # https://stackoverflow.com/a/16476974/6572046
        for index, row in df.iterrows():
            csv_row = []

            for i in range(len(_columns)):
                cell_data = row[_columns[i]]
                if i == 0:
                    csv_row.append(cell_data)
                else:
                    csv_row.append('\n'.join(cell_data))
                    csv_row.append(len(cell_data))

            csv_writer.writerow(csv_row)
