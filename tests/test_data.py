import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import load_sources,morphology_fields
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


if __name__=='__main__':unittest.main()
