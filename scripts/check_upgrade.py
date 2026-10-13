"""Optional integration check using an isolated Anki collection, never a user's profile."""
import argparse
import json
import tempfile
from pathlib import Path
from anki.collection import Collection
from anki.import_export_pb2 import ImportAnkiPackageRequest, ImportAnkiPackageOptions
from common import ROOT


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('previous',type=Path)
    p.add_argument('current',type=Path)
    p.add_argument('--report',type=Path,default=ROOT/'dist/upgrade-validation.json')
    a=p.parse_args();a.report.parent.mkdir(parents=True,exist_ok=True)
    options=ImportAnkiPackageOptions(merge_notetypes=True,update_notes=1,update_notetypes=1,with_scheduling=False)
    with tempfile.TemporaryDirectory(dir=a.report.parent.resolve()) as tmp:
        c=Collection(str(Path(tmp)/'collection.anki2'))
        try:
            def load(path):
                c.import_anki_package(ImportAnkiPackageRequest(package_path=str(path.resolve()),options=options))
            load(a.previous)
            before={tuple(row) for row in c.db.all('select id,nid,ord from cards')}
            card=c.get_card(c.db.scalar('select id from cards limit 1'))
            card.type=2;card.queue=2;card.ivl=5;card.reps=3;card.due=10;c.update_card(card);cid=card.id
            load(a.current)
            assert before=={tuple(row) for row in c.db.all('select id,nid,ord from cards')}
            assert c.card_count()==12155
            card=c.get_card(cid);assert (card.type,card.queue,card.ivl,card.reps,card.due)==(2,2,5,3,10)
            morphology_count=0
            for nid in c.db.list('select id from notes'):
                n=c.get_note(nid)
                assert len(n.fields)==22 and n['Example1'] and n['Translation1']
                assert n['WordAudio'] and not n['Example1Audio'] and not n['Example2Audio']
                assert not n['Example2'] or n['Translation2']
                morphology_count+=bool(n['Morphology'] or n['WordFamily'])
            assert morphology_count==738
            assert '自动转写' not in card.answer() and '未人工校订' not in card.answer()
        finally:
            c.close()
    result={'actual_anki_import':'PASS','cards':12155,'morphology_or_family':morphology_count,
            'existing_card_ids_preserved':True,'simulated_review_schedule_preserved':True,
            'test_collection':'isolated temporary collection; no user profile accessed'}
    a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
