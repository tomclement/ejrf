from django.test import Client
from questionnaire.models import Questionnaire, Section
from questionnaire.tests.base_test import BaseTest


class HomePageViewTest(BaseTest):

    def setUp(self):
        self.client = Client()
        self.user, self.country = self.create_user_with_no_permissions()
        self.assign('can_submit_responses', self.user)
        self.client.login(username=self.user.username, password='pass')

    def test_get(self):
        response = self.client.get("/")
        self.assertEqual(200, response.status_code)
        templates = [template.name for template in response.templates]
        self.assertIn('home/index.html', templates)

    def test_homepage_redirects_to_first_section_of_first_questionnaire_if_any_if_logged_in_as_data_submitter(self):
        questionnaire = Questionnaire.objects.create(name="JRF", description="bla")
        section = Section.objects.create(title="section", order=1, questionnaire=questionnaire, name="section")
        Section.objects.create(title="section", order=2, questionnaire=questionnaire, name="section")

        response = self.client.get("/")
        expected_url = "/questionnaire/entry/%d/section/%d/" % (questionnaire.id, section.id)
        self.assertRedirects(response, expected_url=expected_url)

    def test_login_required_for_home_get(self):
        self.assert_login_required('/')


class GlobalAdminHomePageViewTest(BaseTest):

    def setUp(self):
        self.client = Client()
        self.user, self.country = self.create_user_with_no_permissions()
        self.assign('can_view_users', self.user)
        self.client.login(username=self.user.username, password='pass')

    def test_get(self):
        questionnaire1 = Questionnaire.objects.create(name="JRF Jamaica", description="bla", year=2012, finalized=True)
        questionnaire2 = Questionnaire.objects.create(name="JRF Brazil", description="bla", year=2013, finalized=False)
        Section.objects.create(title="section", order=1, questionnaire=questionnaire1, name="section")
        Section.objects.create(title="section", order=1, questionnaire=questionnaire2, name="section")
        response = self.client.get("/")
        self.assertEqual(200, response.status_code)
        templates = [template.name for template in response.templates]
        self.assertIn('home/global/index.html', templates)
        self.assertIn(questionnaire1, response.context['finalized_questionnaires'])
        self.assertIn(questionnaire2, response.context['draft_questionnaires'])
