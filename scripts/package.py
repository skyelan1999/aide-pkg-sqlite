"""Deterministically package SQLite runtime; never overwrite changed released bytes."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check',action='store_true')
args=parser.parse_args()
version=json.loads((root/'manifest.json').read_text(encoding='utf-8'))['version']
name='aide-pkg-sqlite-v'+version+'.zip'
output=root/'packages'/('v'+version)
buffer=io.BytesIO()
with zipfile.ZipFile(buffer,'w') as bundle:
    for source in ('LICENSE','index.js','manifest.json','test.js','security.test.cjs'):
        item=zipfile.ZipInfo(source,(2026,1,1,0,0,0))
        item.compress_type=zipfile.ZIP_DEFLATED
        item.external_attr=0o100644<<16
        bundle.writestr(item,(root/source).read_bytes())
raw=buffer.getvalue()
sums=hashlib.sha256(raw).hexdigest()+'  '+name+'\n'
if args.check:
    assert (output/name).read_bytes()==raw,'Runtime ZIP differs from reviewed source'
    assert (output/'SHA256SUMS').read_text()==sums,'Package digest differs'
else:
    output.mkdir(parents=True,exist_ok=True)
    if (output/name).exists() and (output/name).read_bytes()!=raw:
        raise ValueError('Bump the plugin version before changing an existing package')
    (output/name).write_bytes(raw)
    (output/'SHA256SUMS').write_text(sums)
print('PASS:',name,len(raw),'bytes',hashlib.sha256(raw).hexdigest())
