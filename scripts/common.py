"""Shared source loading and rendering, with no Anki profile access."""
import html
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_sources():
    config = json.loads((ROOT / 'deck-source/config.json').read_text(encoding='utf-8'))
    notes = [json.loads(line) for path in sorted((ROOT / 'deck-source').glob('192*.jsonl'))
             for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    morphology = json.loads((ROOT / 'deck-source/morphology.json').read_text(encoding='utf-8'))
    return config, notes, morphology


def morphology_fields(word, entries):
    item = entries.get(html.unescape(word).lower(), {})
    parts = item.get('parts', [])
    rendered = '<span class="morph-plus"> + </span>'.join(
        '<span class="morpheme"><b>' + html.escape(p['form']) + '</b> '
        '<small>' + html.escape(p['meaning']) + '</small></span>' for p in parts)
    family = ' · '.join(html.escape(w) for w in item.get('family', []))
    if html.unescape(word).lower() == 'mission' and item.get('kind') == 'historical_root':
        rendered += '<span class="morph-note">这里的 miss- 是表示“送”的词根，与英语 miss（错过）不同。</span>'
    return rendered, family


def load_enrichment():
    return {row['word'].lower(): row for path in sorted((ROOT/'deck-source/enrichment').glob('*.jsonl'))
            for line in path.read_text(encoding='utf-8').splitlines()
            if (row := json.loads(line))}


def compile_template(name):
    template=(ROOT/'templates'/name).read_text(encoding='utf-8-sig')
    settings=(ROOT/'templates/module-settings.js').read_text(encoding='utf-8-sig')
    version=json.loads((ROOT/'deck-source/config.json').read_text(encoding='utf-8'))['version']
    updates=(ROOT/'templates/update-check.js').read_text(encoding='utf-8-sig')
    return (template.replace('<!-- MODULE_SETTINGS -->','<script>\n'+settings+'\n</script>')
            .replace('<!-- UPDATE_CHECK -->','<script>\n'+updates+'\n</script>')
            .replace('__DECK_VERSION__',version))


def extra_fields(word, enrichment):
    data=enrichment.get(html.unescape(word).lower(),{})
    definition=html.escape(data.get('english_definition',''))
    derivatives=data.get('derivatives',[])
    derivative_html=''
    if derivatives:
        derivative_html='<dl class="derivative-list">'+''.join(
            '<div class="derivative-row"><dt lang="en">'+html.escape(d['word'])+'</dt><dd>'+
            html.escape(d['meaning'])+' <small>· '+html.escape(d['relation'])+'</small></dd></div>'
            for d in derivatives)+'</dl>'
    refs=data.get('exam_references',[])
    if not refs:return definition,derivative_html,''
    groups=defaultdict(list)
    quotes=[]
    for ref in refs:
        book=re.sub(r'^剑(?:雅|桥雅思)?\s*(\d+)$',r'剑桥雅思 \1',ref['book'])
        groups[(book,ref['category'])].append(ref)
        if ref.get('short_quote'):
            text=html.escape(ref['short_quote'])
            text=re.sub(r'(?<!\w)'+re.escape(html.escape(word))+r'(?!\w)',lambda m:'<strong>'+m[0]+'</strong>',text,flags=re.I)
            quotes.append('<blockquote class="exam-quote"><div class="en" lang="en">…'+text+'…</div><div class="cn">'+
                html.escape(ref.get('quote_translation',''))+'</div><cite class="exam-location">'+html.escape(book+' · '+ref['location']+' · '+ref['category'])+'</cite></blockquote>')
    body=''.join(quotes)+'<p class="exam-summary">按词形检索的真题出处。展开书目查看卷次与题目位置；完整语境请核对原题。</p>'
    for (book,category),rows in sorted(groups.items()):
        # Keep all source locations; alias normalization does not claim new evidence.
        merged={}
        for r in rows:
            identity=(r['location'],r['form'])
            merged.setdefault(identity,set()).update(r['sentence_hashes'])
        body+='<details class="exam-book"><summary>'+html.escape(book+' · '+category)+' · '+str(len(merged))+' 处</summary><ol>'
        for (location,form),hashes in sorted(merged.items()):
            body+='<li>'+html.escape(location)+' · <span lang="en">'+html.escape(form)+'</span> · '+str(len(hashes))+' 条匹配</li>'
        body+='</ol></details>'
    return definition,derivative_html,body
