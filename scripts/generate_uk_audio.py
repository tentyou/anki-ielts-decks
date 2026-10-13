"""Generate resumable offline UK word MP3s on Windows with installed Hazel TTS."""
import argparse,concurrent.futures,hashlib,html,json,subprocess
from pathlib import Path
from common import ROOT,load_sources
p=argparse.ArgumentParser()
p.add_argument('--media-dir',type=Path,default=ROOT/'media')
p.add_argument('--jobs',type=int,default=4)
p.add_argument('--ffmpeg',default='ffmpeg')
a=p.parse_args()
assert 1<=a.jobs<=8
folder=a.media_dir.resolve();folder.mkdir(parents=True,exist_ok=True)
queue_dir=ROOT/'work/uk-audio-queues';queue_dir.mkdir(parents=True,exist_ok=True)
notes=load_sources()[1];words={};items=[]
for note in notes:
 word=html.unescape(note['fields']['Word'])
 digest=hashlib.sha256(('HazelDesktop|en-GB|rate=-1|mp3-32k-24khz-trim-v1|'+word).encode()).hexdigest()[:24]
 name='tts_uk_'+digest+'.mp3';words[word.lower()]=name;items.append({'text':word,'path':str(folder/name)})
def run(i):
 queue=queue_dir/(str(i)+'.json');queue.write_text(json.dumps(items[i::a.jobs],ensure_ascii=False),encoding='utf-8')
 subprocess.run(['powershell.exe','-NoProfile','-File',str(ROOT/'scripts/synthesize_uk_words.ps1'),'-QueueFile',str(queue),'-FfmpegPath',a.ffmpeg],check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:list(pool.map(run,range(a.jobs)))
manifest={}
for name in sorted(words.values()):
 content=(folder/name).read_bytes();assert len(content)>1000,name
 manifest[name]={'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()}
meta={'voice':'Microsoft Hazel Desktop','locale':'en-GB','rate':-1,'format':'MP3 mono 24kHz 32kbps; edge silence trimmed','words':words}
(ROOT/'deck-source/audio-uk.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'deck-source/media-manifest-uk.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(manifest),'bytes':sum(x['bytes'] for x in manifest.values()),'voice':meta['voice']},ensure_ascii=False),flush=True)
