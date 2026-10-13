"""Extract only manifest-listed MP3 files from an existing release."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from common import ROOT

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('package',type=Path)
    p.add_argument('--output',type=Path,default=ROOT/'media');a=p.parse_args()
    manifest=json.loads((ROOT/'deck-source/media-manifest.json').read_text(encoding='utf-8'))
    manifest.update(json.loads((ROOT/'deck-source/media-manifest-uk.json').read_text(encoding='utf-8')))
    a.output.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.package) as z:
        mapping=json.loads(z.read('media'))
        for key,name in mapping.items():
            if name not in manifest:continue
            assert Path(name).name==name and name.endswith('.mp3')
            content=z.read(key)
            assert hashlib.sha256(content).hexdigest()==manifest[name]['sha256']
            (a.output/name).write_bytes(content)
    assert all((a.output/name).exists() for name in manifest)
    print(f'Extracted {len(manifest)} word recordings.')
