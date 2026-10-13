"""Structural and known semantic regressions. This is not a semantic oracle."""
import html
import json
import re
from common import ROOT, load_sources, load_enrichment


def validate():
    config, notes, morphology = load_sources()
    assert len(notes) == 12155
    assert len({n['guid'] for n in notes}) == len(notes)
    assert len({n['fields']['Word'].lower() for n in notes}) == len(notes)
    sentences = 0
    by_word = {}
    refs = set()
    for note in notes:
        fields = note['fields']
        by_word[html.unescape(fields['Word']).lower()] = fields
        assert str(note['deck_id']) in config['decks']
        assert fields['Word'] and fields['IPA'] and fields['Meaning']
        assert fields['Example1'] and fields['Translation1']
        assert not fields['Example2'] or fields['Translation2']
        assert not fields['Example1Audio'] and not fields['Example2Audio']
        assert not fields['IPANote'] and not fields['EntryNote']
        refs.update(re.findall(r'\[sound:([^\]]+)\]', fields['WordAudio']))
        sentences += bool(fields['Example1']) + bool(fields['Example2'])
        for tag in note['tags']:
            assert ' ' not in tag
    for word, required, forbidden in [
        ('crane', '起重机', '鹤|鶴'), ('organ', '器官', '风琴|風琴'),
        ('drill', '钻机', '演习|演習'), ('bill', '账单', '比尔|比爾'),
        ('mole', '鼹鼠', '痣'), ('china', '瓷器', '中国|中國'),
        ('sue', '起诉', '苏在|蘇在'), ('kindle', '生火', '阅读器|Kindle'),
        ('tire', '疲倦', '轮胎|輪胎'), ('plays', '戏剧', '打高尔夫'),
    ]:
        text = html.unescape(by_word[word]['Translation1'] + by_word[word]['Translation2'])
        assert required in text, (word, text)
        assert not re.search(forbidden, text), (word, text)
    for word, item in morphology.items():
        assert word in by_word, word
        assert item['source'].startswith('https://')
        for part in item['parts']:
            assert part['form'] and part['meaning'] and part['type'] in {'base', 'root', 'prefix', 'suffix'}
        assert word not in item['family']
    for word in ['liver', 'career', 'station', 'shower', 'minor', 'passion', 'liable']:
        assert not morphology.get(word, {}).get('parts'), word
    assert morphology['interdependent']['parts'][0]['form'] == 'inter-'
    assert [p['form'] for p in morphology['reusable']['parts']] == ['re-', 'use', '-able']
    assert any(p['form']=='miss-' and '送' in p['meaning'] for p in morphology['mission']['parts'])
    enrichment=load_enrichment()
    assert len(enrichment)==11798 and set(enrichment)<=set(by_word)
    quotes=[]
    for word,item in enrichment.items():
        for derivative in item['derivatives']:
            assert derivative['word'] and derivative['meaning']
            assert derivative['word'].lower()!=word
        for ref in item['exam_references']:
            assert ref['book'] and ref['location'] and ref['form']
            assert ref['occurrences']==len(ref['sentence_hashes'])
            assert all(re.fullmatch('[a-f0-9]{20}',x) for x in ref['sentence_hashes'])
            assert 'sentence' not in ref and 'text' not in ref
            if ref.get('short_quote'):quotes.append(ref['short_quote'])
    assert sum(len(re.findall(r"[A-Za-z]+",q)) for q in quotes)==9
    switches=dict(re.findall(r'(\w+): (true|false)',(ROOT/'templates/module-settings.js').read_text(encoding='utf-8-sig')))
    assert len(switches)==11 and set(switches.values())=={'true'}
    assert len(refs) == 12155
    for path in (ROOT / 'templates').iterdir():
        text = path.read_text(encoding='utf-8')
        assert '{{tts ' not in text
        assert 'Example1Audio' not in text and 'Example2Audio' not in text
        assert '未人工校订' not in text and '自动转写' not in text
    return {'notes': len(notes), 'examples': sentences, 'morphology_or_family': len(morphology),
            'word_audio_files': len(refs), 'sentence_audio_files': 0,
            'english_definitions':sum(bool(x['english_definition']) for x in enrichment.values()),
            'derivative_entries':sum(bool(x['derivatives']) for x in enrichment.values()),
            'exam_index_entries':sum(bool(x['exam_references']) for x in enrichment.values())}


if __name__ == '__main__':
    print(json.dumps(validate(), ensure_ascii=False, indent=2))
