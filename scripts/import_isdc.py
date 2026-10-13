"""Import reviewed ISDC modules from a locally decoded public snapshot.

Raw exam sentences are read only to check forms and derive hashes, never exported.
Requires requirements-import.txt. Run from any directory; root data stays in repo.
"""
import argparse,json,re,html,hashlib,collections
from pathlib import Path
from lemminflect import getAllInflections,getAllLemmas
from common import ROOT,load_sources
parser=argparse.ArgumentParser()
parser.add_argument('snapshot',type=Path,help='JSON output from decode_isdc.cjs')
parser.add_argument('--output',type=Path,default=ROOT/'work/isdc-import')
args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
raw=json.loads(args.snapshot.read_text(encoding='utf-8'))
source={w['w'].strip().lower():w for g in raw['g'] for w in g['ws']}
config,records,morph=load_sources()
by={html.unescape(r['fields']['Word']).lower():r for r in records}
D=json.loads((ROOT/'deck-source/definition-overrides.json').read_text(encoding='utf-8'))
def pos(meaning):
 p=set()
 if re.search(r'\bn\.',meaning):p.add('NOUN')
 if re.search(r'\b(?:v|vt|vi)\.',meaning):p.add('VERB')
 if 'adj.' in meaning:p.add('ADJ')
 if 'adv.' in meaning:p.add('ADV')
 return p
rejected=[];added_roots=[];out=[];counts=collections.Counter();quoted=False
for record in records:
 f=record['fields'];word=html.unescape(f['Word']);key=word.lower();s=source.get(key);meaning=html.unescape(f['Meaning']);allowed=pos(meaning)
 if not s:continue
 counts['matched']+=1
 # Clean duplicated or corrupt entries; focused definition edits take priority.
 ed=s.get('ed','').strip();segments=list(dict.fromkeys(x.strip() for x in re.split('[；\n]',ed) if x.strip()))
 segments=[x for x in segments if not any(t in x.lower() for t in ['misspelling','undefined','no meaning','not a word'])]
 ed=segments[0] if segments else ''
 sentences=re.split(r'(?<=[.!?])\s+(?=[A-Z])',ed)
 if sentences:ed=sentences[0]
 if len(ed)>280 or len(ed)<6 or re.search(r'[\u4e00-\u9fff]|https?://',ed):ed=''
 if key in D:ed=D[key];counts['definition_overrides']+=1
 elif ('NOUN' in allowed and len(allowed)==1 and re.match(r'^To\s',ed)) or ('VERB' in allowed and len(allowed)==1 and re.match(r'^(A|An|The) '+re.escape(key)+r'\b',ed,re.I)):
  rejected.append({'word':word,'module':'definition','reason':'英英释义词性不符，未导入'});ed=''
 if ed:counts['definitions']+=1
 # Inflections must come from the intended POS. Other derivatives require a verified family relationship.
 forms={key};lemmas={key}
 for p in allowed:
  lemmas.update(getAllLemmas(key).get(p,()))
  for lemma in list(lemmas):
   for vs in getAllInflections(lemma,upos=p).values():forms.update(v.lower() for v in vs)
 trusted=set(morph.get(key,{}).get('family',[]))
 trusted.update(w for w,v in morph.items() if v.get('base')==key)
 dv=s.get('dv',[])
 if isinstance(dv,list):
  dv=[raw['p']['v'][x] if isinstance(x,int) else x for x in dv]
  clean_dv=[]
  for x in dv:
   try: clean_dv.append(json.loads(x) if isinstance(x,str) else x)
   except (ValueError,TypeError): pass
  dv=clean_dv
 else:dv=[]
 derivatives=[];seen=set()
 for d in dv:
  if not isinstance(d,dict):continue
  form=str(d.get('word','')).strip();k=form.lower()
  if not form or k==key or k in seen:continue
  if k in forms:
   definition=meaning;relation='屈折变化'
  elif k in trusted and k in by:
   definition=html.unescape(by[k]['fields']['Meaning']);relation='派生或同族词'
  else:continue
  derivatives.append({'word':form,'meaning':definition,'relation':relation});seen.add(k)
 for k in sorted(trusted):
  if k in seen or k==key or k not in by:continue
  derivatives.append({'word':html.unescape(by[k]['fields']['Word']),'meaning':html.unescape(by[k]['fields']['Meaning']),'relation':'派生或同族词'});seen.add(k)
 if derivatives:counts['derivative_entries']+=1;counts['derivatives']+=len(derivatives)
 # Keep complete location indexes, not a redistribution of an entire copyrighted test corpus.
 groups={};exam_excluded=0
 for form_idx,entries in s.get('dt',{}).items():
  form=raw['p']['k'][int(form_idx)] if form_idx.isdigit() else form_idx
  if form.lower() not in forms:
   counts['excluded_exam_matches']+=len(entries)
   continue
  for a in entries:
   text=raw['p']['s'][a[0]]
   if not re.search(r'(?<!\w)'+re.escape(form)+r'(?!\w)',text,re.I):
    exam_excluded+=1;continue
   if key in {'sue','bill','frank','ally','kindle','potter'}:
    if re.search(r'(?<!\w)'+re.escape(key.title())+r'(?!\w)',text) or re.search(r'\b'+key.upper()+r'\s*:',text):exam_excluded+=1;continue
   if key=='china' and re.search(r'\bChina\b',text):exam_excluded+=1;continue
   if key=='may' and not re.search(r'\bMay\b',text):exam_excluded+=1;continue
   if key=='crane' and re.search(r'\b(?:bird|paper|feather|wings?|neck)\b',text,re.I):exam_excluded+=1;continue
   book=raw['d']['n'][a[1]] if a[1]>=0 else ''
   location=raw['d']['p'][a[2]] if a[2]>=0 else ''
   category=raw['d']['y'][a[3]] if a[3]>=0 else ''
   if not book or not location:exam_excluded+=1;continue
   identity=(book,location,category,form)
   group=groups.setdefault(identity,{'book':book,'location':location,'category':category,'form':form,'sentence_hashes':set()})
   digest=hashlib.sha256(text.encode()).hexdigest()[:20];group['sentence_hashes'].add(digest)
   if key=='crane' and not quoted and 'lifted into position in five large sections by crane' in text:
    group['short_quote']='lifted into position in five large sections by crane'
    group['quote_translation']='用起重机分五个大型部分吊装到位';quoted=True
   counts['exam_matches']+=1
 exam=[]
 for group in groups.values():
  group['sentence_hashes']=sorted(group['sentence_hashes']);group['occurrences']=len(group['sentence_hashes']);exam.append(group)
 if exam:counts['exam_entries']+=1;counts['exam_locations']+=len(exam)
 counts['excluded_exam_matches']+=exam_excluded
 out.append({'word':word,'english_definition':ed,'definition_source':'ISDC，已去重整理；重点词义另行改写' if ed else '', 'derivatives':derivatives,'exam_references':exam,'source':'https://isdc.pages.dev/'})
# Only write candidate outputs; semantic review is required before replacing sources.
by_deck=collections.defaultdict(list)
for item in out:
    by_deck[by[item['word'].lower()]['deck_id']].append(item)
for deck,items in by_deck.items():
    (args.output/(str(deck)+'.jsonl')).write_text(''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n' for x in items),encoding='utf-8')
report={**counts,'short_quote_words':9,'limitations':'Automatic structural filters and focused overrides; not exhaustive semantic review.'}
(args.output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
