"""Shared source loading and rendering, with no Anki profile access."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_sources():
    config = json.loads((ROOT / 'deck-source/config.json').read_text(encoding='utf-8'))
    notes = [json.loads(line) for path in sorted((ROOT / 'deck-source').glob('*.jsonl'))
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
    return rendered, family
