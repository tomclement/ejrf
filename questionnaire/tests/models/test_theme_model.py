from questionnaire.models.themes import Theme
from questionnaire.tests.base_test import BaseTest


class ThemeTest(BaseTest):

    def test_user_fields(self):
        theme = Theme()
        fields = [str(item.attname) for item in theme._meta.fields]
        self.assertEqual(5, len(fields))
        for field in ['id', 'created', 'modified', 'name', 'description']:
            self.assertIn(field, fields)

    def test_theme_stores(self):
        theme = Theme.objects.create(name="Theme1", description="Our theme.")
        self.failUnless(theme.id)

    def test_theme_unicode(self):
        theme = Theme.objects.create(name="Theme1", description="Our theme.")
        self.assertEqual(str(theme), "Theme1".encode('utf8'))