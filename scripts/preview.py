"""Render a static card preview using the actual fields and templates."""
import argparse
import html
import re
from pathlib import Path
from common import ROOT, load_sources, morphology_fields, load_enrichment, extra_fields, compile_template


def render(template,fields):
    for _ in range(4):
        template=re.sub(r'{{([#^])(\w+)}}(.*?){{/\2}}',
            lambda m:m[3] if bool(fields.get(m[2]))==(m[1]=='#') else '',template,flags=re.S)
    template=re.sub(r'{{(\w+)}}',lambda m:fields.get(m[1],''),template)
    return re.sub(r'\[sound:([^\]]+)\]', '<span class="preview-audio">▶ 单词发音</span>',template)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--word',default='interdependent')
    p.add_argument('--output',type=Path,default=ROOT/'dist/preview.html');a=p.parse_args()
    _,notes,m=load_sources();f=dict(next(n['fields'] for n in notes if n['fields']['Word'].lower()==a.word.lower()))
    f['Morphology'],f['WordFamily']=morphology_fields(f['Word'],m)
    f['EnglishDefinition'],f['Derivatives'],f['ExamExamples']=extra_fields(f['Word'],load_enrichment())
    css=(ROOT/'templates/style.css').read_text(encoding='utf-8')
    back=render(compile_template('back.html'),f)
    doc='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Card preview</title><style>'+css+'.preview-audio{font-size:13px;color:#607d91;padding:4px 0}</style><body class="card">'+back+'</body></html>'
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text('\n'.join(line.rstrip() for line in doc.splitlines())+'\n',encoding='utf-8')
