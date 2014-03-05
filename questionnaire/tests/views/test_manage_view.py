from django.core.urlresolvers import reverse
from django.test import Client
from questionnaire.forms.questionnaires import QuestionnaireFilterForm
from questionnaire.models import Questionnaire, Section, Organization, Region
from questionnaire.tests.base_test import BaseTest


class ManageJRFViewTest(BaseTest):

    def setUp(self):
        self.client = Client()
        self.user, self.country = self.create_user_with_no_permissions()
        self.assign('can_edit_questionnaire', self.user)
        self.client.login(username=self.user.username, password='pass')

    def test_get(self):
        questionnaire1 = Questionnaire.objects.create(name="JRF Jamaica", description="bla", year=2012, status=Questionnaire.FINALIZED)
        questionnaire2 = Questionnaire.objects.create(name="JRF Brazil", description="bla", year=2013, status=Questionnaire.DRAFT)
        Section.objects.create(title="section", order=1, questionnaire=questionnaire1, name="section")
        Section.objects.create(title="section", order=1, questionnaire=questionnaire2, name="section")
        response = self.client.get("/manage/")
        self.assertEqual(200, response.status_code)
        templates = [template.name for template in response.templates]
        self.assertIn('home/global/index.html', templates)
        self.assertIn(questionnaire1, response.context['finalized_questionnaires'])
        self.assertIn(questionnaire2, response.context['draft_questionnaires'])
        self.assertIsInstance(response.context['filter_form'], QuestionnaireFilterForm)
        self.assertEqual(reverse('duplicate_questionnaire_page'), response.context['action'])


class FinalizeQuestionnaireViewTest(BaseTest):

    def setUp(self):
        self.client = Client()
        self.user, self.country = self.create_user_with_no_permissions()
        self.assign('can_edit_questionnaire', self.user)
        self.client.login(username=self.user.username, password='pass')

        self.questionnaire = Questionnaire.objects.create(name="JRF Brazil", description="bla", year=2013, status=Questionnaire.DRAFT)
        Section.objects.create(title="Cured Cases of Measles", order=1, questionnaire=self.questionnaire, name="Cured Cases")
        self.url = '/questionnaire/%d/finalize/' % self.questionnaire.id

    def test_post_finalizes_questionnaire(self):
        self.client.post(self.url)
        self.assertNotIn(self.questionnaire, Questionnaire.objects.filter(status=Questionnaire.DRAFT).all())
        self.assertIn(self.questionnaire, Questionnaire.objects.filter(status=Questionnaire.FINALIZED).all())

    def test_post_unfinalizes_questionnaire(self):
        questionnaire = Questionnaire.objects.create(name="JRF Brazil", description="bla", year=2013, status=Questionnaire.FINALIZED)
        url = '/questionnaire/%d/unfinalize/' % questionnaire.id

        self.client.post(url)
        self.assertNotIn(questionnaire, Questionnaire.objects.filter(status=Questionnaire.FINALIZED).all())
        self.assertIn(questionnaire, Questionnaire.objects.filter(status=Questionnaire.DRAFT).all())


class PublishQuestionnaireToRegionsViewTest(BaseTest):

    def setUp(self):
        self.client = Client()
        self.user, self.country = self.create_user_with_no_permissions()
        self.assign('can_edit_questionnaire', self.user)
        self.client.login(username=self.user.username, password='pass')

        self.questionnaire = Questionnaire.objects.create(name="JRF Brazil", description="bla", year=2013, status=Questionnaire.FINALIZED)
        Section.objects.create(title="Cured Cases of Measles", order=1, questionnaire=self.questionnaire, name="Cured Cases")

        self.url = '/questionnaire/%d/publish/' % self.questionnaire.id
        self.who = Organization.objects.create(name="WHO")
        self.unicef = Organization.objects.create(name="UNICEF")
        self.australia = Region.objects.create(name="Australia", organization=self.who)

    def test_post_publishes_questionnaire(self):
        afro = Region.objects.create(name="The Afro", organization=self.who)
        paho = Region.objects.create(name="The Paho", organization=self.who)
        pacific = Region.objects.create(name="haha", organization=self.who)
        asia = Region.objects.create(name="hehe", organization=self.who)
        questionnaire = Questionnaire.objects.create(name="JRF Brazil", description="bla", year=2013, status=Questionnaire.FINALIZED, region=afro)
        Section.objects.create(title="Cured Cases of Measles", order=1, questionnaire=questionnaire, name="Cured Cases")
        Region.objects.create(name="UNICEF ASIA", organization=self.unicef)

        data = {'regions': [paho.id, pacific.id, asia.id,]}

        response = self.client.post(self.url, data=data)
        self.assertRedirects(response, reverse('manage_jrf_page'))
        message = "The questionnaire has been published to %s, %s, %s" % (paho.name, pacific.name, asia.name)
        self.assertIn(message, response.cookies['messages'].value)
        questionnaires = Questionnaire.objects.filter(year=self.questionnaire.year)
        self.assertEqual(5, questionnaires.count())
        [self.assertEqual(1, region.questionnaire.all().count()) for region in [paho, pacific, asia]]
        self.assertEqual(1, afro.questionnaire.all().count())

    def test_post_publishes_questionnaire_with_errors(self):
        data = {'regions': []}
        response = self.client.post(self.url, data=data)
        self.assertRedirects(response, reverse('manage_jrf_page'))
        message = "Questionnaire could not be published see errors below"
        self.assertIn(message, response.cookies['messages'].value)