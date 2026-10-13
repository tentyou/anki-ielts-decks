import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import load_sources,morphology_fields,extra_fields,load_enrichment,compile_template
from validate import validate


class DeckTests(unittest.TestCase):
    def test_data_and_regressions(self):
        self.assertEqual(validate()['notes'],12155)

    def test_optional_sections_and_safe_html(self):
        _,_,m=load_sources()
        self.assertEqual(morphology_fields('crane',m),('',''))
        body,family=morphology_fields('interdependent',m)
        self.assertIn('inter-',body)
        self.assertIn('depend',family)
        malicious={'x':{'parts':[{'form':'<script>','meaning':'a & b','type':'base'}],'family':['<img>']}}
        body,family=morphology_fields('x',malicious)
        self.assertNotIn('<script>',body)
        self.assertIn('&lt;img&gt;',family)

    def test_rich_modules_and_escaping(self):
        e=load_enrichment()
        definition,derived,exam=extra_fields('crane',e)
        self.assertTrue(definition)
        self.assertIn('用起重机',exam)
        self.assertIn('Test 1 Passage 2',exam)
        self.assertNotIn('paper crane',exam)
        definition,derived,exam=extra_fields('x',{'x':{'english_definition':'<script>',
            'derivatives':[{'word':'<img>','meaning':'a & b','relation':'<x>'}],
            'exam_references':[{'book':'<x>','category':'<x>','location':'<x>','form':'x','sentence_hashes':['abc']}]}})
        self.assertEqual(definition,'&lt;script&gt;')
        self.assertNotIn('<img>',derived)
        self.assertNotIn('<x>',exam)
        self.assertEqual(extra_fields('nonexistent',e),('','',''))

    def test_template_compilation_and_module_order(self):
        back=compile_template('back.html')
        self.assertNotIn('<!-- MODULE_SETTINGS -->',back)
        self.assertIn('var modules',back)
        self.assertLess(back.index('data-module="examples"'),back.index('data-module="examExamples"'))
        _,_,m=load_sources()
        for word in ['income','legal','insurance']:
            self.assertFalse(m.get(word,{}).get('parts'),word)


if __name__=='__main__' :unittest.main()
