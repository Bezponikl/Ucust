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

    print(f'[FixComfy] Total comfy_kitchen files patched: {patched_count}')

    # 2. Patch ComfyUI-LTXVideo kornia.geometry.transform.pyramid import issue
    ltx_custom_nodes = [
        '/opt/ucust/ComfyUI/custom_nodes/ComfyUI-LTXVideo/pyramid_blending.py',
        'ComfyUI/custom_nodes/ComfyUI-LTXVideo/pyramid_blending.py',
        '../ComfyUI/custom_nodes/ComfyUI-LTXVideo/pyramid_blending.py'
    ]
    for p in ltx_custom_nodes:
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Restore any broken variable names
                content = content.replace("0_right", "pad_right").replace("0_down", "pad_down")
                if "from torch.nn.functional import pad" not in content:
                    content = "from torch.nn.functional import pad\n" + content
                # Remove pad only from the kornia import list
                content = content.replace("    pad,\n", "\n").replace("    pad,", "")
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'[FixComfy] ✅ Successfully patched ComfyUI-LTXVideo pyramid_blending.py at {p}')
            except Exception as e:
                print(f'[FixComfy] Error patching LTXVideo: {e}')

    # 3. Sync Ltx_generations.json into ComfyUI internal workflow folders
    src_json = 'ai/Ltx_generations.json'
    if not os.path.exists(src_json):
        src_json = '/opt/ucust/ai/Ltx_generations.json'
    if os.path.exists(src_json):
        import shutil
        target_dirs = [
            '/opt/ucust/ComfyUI/user/default/workflows',
            '/opt/ucust/ComfyUI/user/workflows',
            'ComfyUI/user/default/workflows',
            'ComfyUI/user/workflows'
        ]
        for td in target_dirs:
            try:
                os.makedirs(td, exist_ok=True)
                dest = os.path.join(td, 'Ltx_generations.json')
                shutil.copy2(src_json, dest)
                print(f'[FixComfy] 📋 Synced workflow to {dest}')
            except Exception as e:
                pass

if __name__ == '__main__':
    fix()
