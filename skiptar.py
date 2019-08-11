#!/usr/bin/env python3

import fileinput
import requests
import sys
import tarfile
import tqdm
import io

def get_all(url, files):
    idx = 0
    head = requests.head(url, allow_redirects=True)
    length = int(head.headers['Content-Length'])
    round_up = lambda x: (x + 511) // 512 * 512

    pbar = tqdm.tqdm(total=length)
    while idx < length:
        response = requests.get(url, headers={'Range': 'bytes={}-{}'.format(idx, idx + 511)})
        idx += 512
        tarinfo = tarfile.TarInfo.frombuf(response.content, 'utf-8', 'strict')
        if tarinfo.name in files:
            pbar.write('Writing {}'.format(tarinfo.name))
            fresponse = requests.get(url, headers={'Range': 'bytes={}-{}'.format(idx, idx + tarinfo.size - 1)})

            tfile = tarfile.TarFile(fileobj=io.BytesIO(response.content + fresponse.content))
            tfile.extractall()

        idx += round_up(tarinfo.size)
        pbar.update(512 + round_up(tarinfo.size))
    pbar.close()

if __name__ == '__main__':
    fs = [x.strip() for x in fileinput.input(sys.argv[2:])]
    get_all(sys.argv[1], fs)
