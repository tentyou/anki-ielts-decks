"""Structural and known semantic regressions. This is not a semantic oracle."""
import html
import json
import re
from common import ROOT, load_sources


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
            assert part['form'] and part['meaning'] and part['type'] in {'base', 'prefix', 'suffix'}
        assert word not in item['family']
    for word in ['liver', 'career', 'mission', 'station', 'shower', 'minor', 'passion', 'liable']:
        assert not morphology.get(word, {}).get('parts'), word
    assert morphology['interdependent']['parts'][0]['form'] == 'inter-'
    assert [p['form'] for p in morphology['reusable']['parts']] == ['re-', 'use', '-able']
    assert len(refs) == 12155
    for path in (ROOT / 'templates').iterdir():
        text = path.read_text(encoding='utf-8')
        assert '{{tts ' not in text
        assert 'Example1Audio' not in text and 'Example2Audio' not in text
        assert '未人工校订' not in text and '自动转写' not in text
    return {'notes': len(notes), 'examples': sentences, 'morphology_or_family': len(morphology),
            'word_audio_files': len(refs), 'sentence_audio_files': 0}


if __name__ == '__main__':
    print(json.dumps(validate(), ensure_ascii=False, indent=2))
