import unittest
from aftertone.full_research import execute_queries,score_coverage
from aftertone.writer import build_prompt
class FullResearchTests(unittest.TestCase):
 def test_missing_search_is_not_fake_pass(self):
  p=execute_queries("虚构艺人","虚构专辑",search=None,pause=0)
  c=score_coverage(p)
  self.assertFalse(c["eight_rounds_executed"])
  self.assertGreater(c["config_required"],20)
 def test_all_rounds_with_mock_search(self):
  p=execute_queries("Singer","Album",search=lambda q:[{"url":"https://example.org/"+str(len(q)),"title":"Source","snippet":"Sample"}],pause=0)
  c=score_coverage(p)
  self.assertTrue(c["eight_rounds_executed"])
  self.assertGreaterEqual(c["executed"],32)
 def test_writer_prompt_cannot_create_listening_claims(self):
  p=build_prompt([],[],[])
  self.assertIn("没有编辑听音",p["rules"])
if __name__=="__main__":unittest.main()
