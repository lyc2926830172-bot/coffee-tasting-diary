import os
import tempfile
import unittest

TEST_DATABASE = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
TEST_DATABASE.close()
os.environ["COFFEE_DIARY_DATABASE"] = TEST_DATABASE.name

from app import app, db, CoffeeBean, TastingNote

class CoffeeDiaryTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()
    def tearDown(self):
        with app.app_context(): db.session.remove(); db.drop_all()
    def test_main_pages_load(self):
        for path in ("/", "/beans", "/notes", "/insights", "/export/diary.csv"): self.assertEqual(self.client.get(path).status_code, 200)
    def test_save_bean_and_note(self):
        self.assertEqual(self.client.post("/beans", data={"name":"测试豆", "origin":"哥伦比亚", "roast_level":"中浅烘焙"}).status_code, 302)
        with app.app_context(): bean = CoffeeBean.query.filter_by(name="测试豆").first()
        response = self.client.post("/notes", data={"bean_id":bean.id, "brewing_method":"手冲", "flavor_notes":"柑橘、焦糖", "acidity":4, "sweetness":4, "body":3, "aftertaste":4, "overall_score":4})
        self.assertEqual(response.status_code, 302)
        with app.app_context(): self.assertEqual(TastingNote.query.count(), 1)

if __name__ == "__main__": unittest.main()
