"""Build an APKG from reviewable source files. Never opens a user collection."""
import argparse
import hashlib
import html
import json
import re
import sqlite3
import tempfile
import time
import zipfile
from pathlib import Path
import genanki
from common import ROOT, load_sources, morphology_fields, load_enrichment, extra_fields, compile_template
from validate import validate


def build(output, media_dir, text_only=False):
    stats = validate()
    config, notes, morphology = load_sources()
    enrichment=load_enrichment()
    model = genanki.Model(config['model_id'], config['model_name'],
        fields=[{'name':name} for name in config['fields']],
        templates=[{'name':'英文 → 中文',
            'qfmt':compile_template('front.html'),
            'afmt':compile_template('back.html')}],
        css=(ROOT/'templates/style.css').read_text(encoding='utf-8'))
    decks = {int(did):genanki.Deck(int(did), data['name']) for did,data in config['decks'].items()}
    media = set()
    manifest = json.loads((ROOT/'deck-source/media-manifest.json').read_text(encoding='utf-8'))
    for record in notes:
        fields = dict(record['fields'])
        fields['Morphology'],fields['WordFamily'] = morphology_fields(fields['Word'],morphology)
        fields['EnglishDefinition'],fields['Derivatives'],fields['ExamExamples']=extra_fields(fields['Word'],enrichment)
        if text_only:
            fields['WordAudio']=''
        else:
            for name in re.findall(r'\[sound:([^\]]+)\]',fields['WordAudio']):
                path=media_dir/name
                if not path.is_file():raise FileNotFoundError(f'Missing {path}; extract media from a release first.')
                assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest[name]['sha256'],name
                media.add(path)
        tags=set(record['tags'])|{'版本_'+config['version']}
        if fields['Morphology'] or fields['WordFamily']:tags.add('构词_词族')
        note=genanki.Note(model=model,fields=[fields.get(name,'') for name in config['fields']],
                          tags=sorted(tags),guid=record['guid'])
        decks[record['deck_id']].add_note(note)
    output.parent.mkdir(parents=True,exist_ok=True)
    # genanki writes uncompressed ZIP; repack without changing the collection or audio.
    with tempfile.TemporaryDirectory(dir=output.parent.resolve()) as tmp:
        raw=Path(tmp)/'raw.apkg'
        package=genanki.Package(list(decks.values()),media_files=[str(p) for p in sorted(media)])
        previous_tempdir=tempfile.tempdir
        try:
            tempfile.tempdir=tmp
            package.write_to_file(raw)
        finally:
            tempfile.tempdir=previous_tempdir
        staged=Path(tmp)/'compressed.apkg'
        with zipfile.ZipFile(raw) as source,zipfile.ZipFile(staged,'w',zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():target.writestr(item.filename,source.read(item.filename))
        with zipfile.ZipFile(staged) as z:
            assert z.testzip() is None
            mapping=json.loads(z.read('media'))
            db=Path(tmp)/'verify.anki2';db.write_bytes(z.read('collection.anki2'))
            con=sqlite3.connect(db)
            assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
            assert con.execute('select count(*) from notes').fetchone()[0]==12155
            assert con.execute('select count(*) from cards').fetchone()[0]==12155
            refs=set()
            for (raw_fields,) in con.execute('select flds from notes'):
                values=raw_fields.split('\x1f');assert len(values)==len(config['fields'])
                assert values[10] and values[11] and not values[17] and not values[18]
                refs.update(re.findall(r'\[sound:([^\]]+)\]',raw_fields))
            assert refs==set(mapping.values())
            con.close()
        output.write_bytes(staged.read_bytes())
    stats.update(version=config['version'],bytes=output.stat().st_size,
                 sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                 packaged_audio_files=len(media),text_only=text_only)
    output.with_suffix('.validation.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
    template_dir=output.parent/'templates';template_dir.mkdir(exist_ok=True)
    for name in ['front.html','back.html']:
        (template_dir/name).write_text(compile_template(name),encoding='utf-8')
    (template_dir/'style.css').write_text((ROOT/'templates/style.css').read_text(encoding='utf-8'),encoding='utf-8')
    print(json.dumps(stats,ensure_ascii=False,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    parser.add_argument('--media-dir',type=Path,default=ROOT/'media')
    parser.add_argument('--text-only',action='store_true')
    args=parser.parse_args()
    if args.output is None:args.output=ROOT/'dist'/('anki-ielts-v'+load_sources()[0]['version']+'.apkg')
    build(args.output,args.media_dir,args.text_only)
