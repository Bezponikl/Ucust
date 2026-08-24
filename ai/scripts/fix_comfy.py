#!/usr/bin/env python3
import sys
import os
import glob
import subprocess

def fix():
    print('[FixComfy] 1. Installing comfy-kitchen in virtualenv...')
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'comfy-kitchen'], check=False)

    site_dirs = [p for p in sys.path if 'site-packages' in p]
    patched_count = 0

    for sdir in site_dirs:
        pattern = os.path.join(sdir, 'comfy_kitchen', '**', '*.py')
        for filepath in glob.glob(pattern, recursive=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    c = f.read()

                orig = c
                if 'kernel_size: list[int]' in c or 'is_causal: list[bool]' in c:
                    c = c.replace('kernel_size: list[int]', 'kernel_size: List[int]')
                    c = c.replace('is_causal: list[bool]', 'is_causal: List[bool]')
                    if 'from typing import' in c:
                        if 'List' not in c:
                            c = c.replace('from typing import ', 'from typing import List, ')
                    else:
                        c = "from typing import List\n" + c

                if c != orig:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(c)
                    print(f'[FixComfy] Patched: {filepath}')
                    patched_count += 1
            except Exception as e:
                print(f'[FixComfy] Error: {e}')

    print(f'[FixComfy] Total files patched: {patched_count}')

if __name__ == '__main__':
    fix()
