from urllib import quote
from django.core.urlresolvers import reverse
from django.test import Client
from questionnaire.forms.questions import QuestionForm
from questionnaire.models import Question, Questionnaire, Section, SubSection, Country, Answer, Region
from questionnaire.tests.base_test import BaseTest


class QuestionViewTest(BaseTest):

    def setUp(self):
        self.client = Client()
        self.user, self.country, self.region = self.create_user_with_no_permissions(region_name=None)

        self.assign('can_edit_questionnaire', self.user)
        self.client.login(username=self.user.username, password='pass')

        self.url = '/questions/'
        self.form_data = {'text': 'How many kids were immunised this year?',
                          'instructions': 'Some instructions',
                          'export_label': 'blah',
                          'answer_type': 'Number'}

    def test_get_list_question(self):
        questions = Question.objects.create(text='B. Number of cases tested',
                                            instructions="Enter the total number of cases", UID='00001',
                                            answer_type='Number')

        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/index.html', templates)
        self.assertIn(questions, response.context['questions'])
        self.assertIsNone(response.context['active_questions'])

    def test_get_list_returns_questions_that_do_not_belong_regions_if_user_is_global_admin(self):
        user = self.assign('can_view_users', self.user)
        region = Region.objects.create(name="some region")
        question1 = Question.objects.create(text='question 1', UID='00001', answer_type='Number', region=region)
        question2 = Question.objects.create(text='question 2', UID='00002', answer_type='Number')
        question3 = Question.objects.create(text='question 3', UID='00003', answer_type='Number')
        self.client.logout()

        client = Client()
        client.login(username=user.username, password="pass")

        response = client.get(self.url)
        self.assertEqual(200, response.status_code)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/index.html', templates)
        self.assertNotIn(question1, response.context['questions'])
        self.assertIn(question2, response.context['questions'])
        self.assertIn(question3, response.context['questions'])

    def test_get_list_question_has_active_questions_from_finalized_questionnaire_in_context(self):
        questions = Question.objects.create(text='B. Number of cases tested', UID='00001', answer_type='Number')

        finalized_questionnaire = Questionnaire.objects.create(status=Questionnaire.FINALIZED, name="finalized")
        section = Section.objects.create(name="section", questionnaire=finalized_questionnaire, order=1)
        subsection = SubSection.objects.create(title="subsection 1", section=section, order=1)
        question1 = Question.objects.create(text='Q1', UID='C00003', answer_type='Number')
        question1.question_group.create(subsection=subsection)

        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/index.html', templates)
        self.assertEqual(2, len(response.context['questions']))
        self.assertIn(questions, response.context['questions'])
        self.assertIn(question1, response.context['questions'])

        self.assertEqual(1, len(response.context['active_questions']))
        self.assertIn(question1, response.context['active_questions'])

    def test_get_create_question(self):
        response = self.client.get(self.url + 'new/')
        self.assertEqual(200, response.status_code)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/new.html', templates)
        self.assertIsNotNone(response.context['form'])
        self.assertEqual('CREATE', response.context['btn_label'])
        self.assertEqual("id-new-question-form", response.context['id'])
        self.assertEqual(reverse('list_questions_page'), response.context['cancel_url'])

    def test_post_create_question(self):
        self.assertRaises(Question.DoesNotExist, Question.objects.get, **self.form_data)
        response = self.client.post(self.url + 'new/', data=self.form_data)
        self.assertRedirects(response, self.url)
        self.failUnless(Question.objects.get(**self.form_data))
        self.assertIn("Question successfully created.", response.cookies['messages'].value)

    def test_post_create_with_invalid_form_returns_errors(self):
        form_data = self.form_data.copy()
        form_data['text'] = ''

        self.assertRaises(Question.DoesNotExist, Question.objects.get, **form_data)
        response = self.client.post(self.url + 'new/', data=form_data)
        self.assertRaises(Question.DoesNotExist, Question.objects.get, **form_data)
        self.assertIn('Question NOT created. See errors below.', response.content)
        self.assertIsInstance(response.context['form'], QuestionForm)
        self.assertEqual("CREATE", response.context['btn_label'])
        self.assertEqual("id-new-question-form", response.context['id'])

    def test_post_multichoice_question_with_options(self):
        form_data = self.form_data.copy()
        form_data['answer_type'] = 'MultiChoice'
        question_options = ['yes, No, Maybe, Nr, Chill']
        self.assertRaises(Question.DoesNotExist, Question.objects.get, **form_data)
        form_data['options'] = question_options
        response = self.client.post(self.url + 'new/', data=form_data)
        self.assertRedirects(response, self.url)
        questions = Question.objects.filter(text=form_data['text'], instructions=form_data['instructions'],
                                            answer_type=form_data['answer_type'])
        self.assertEqual(1, len(questions))
        options = questions[0].options.all()

        self.assertEqual(5, options.count())
        [self.assertIn(option.text, question_options[0].split(',')) for option in options]

    def test_post_multichoice_question_with_options_with_form_errors(self):
        form_data = self.form_data.copy()
        form_data['answer_type'] = 'MultiChoice'
        self.assertRaises(Question.DoesNotExist, Question.objects.get, **form_data)
        form_data['options'] = []
        response = self.client.post(self.url + 'new/', data=form_data)
        self.assertRaises(Question.DoesNotExist, Question.objects.get, text=form_data['text'], instructions=form_data['instructions'], answer_type=form_data['answer_type'])
        self.assertIn('Question NOT created. See errors below.', response.content)
        self.assertIsInstance(response.context['form'], QuestionForm)
        self.assertEqual("CREATE", response.context['btn_label'])
        self.assertEqual("id-new-question-form", response.context['id'])

    def test_delete_question(self):
        data = {'text': 'B. Number of cases tested',
                'instructions': "Enter the total number of cases",
                'UID': '00001', 'answer_type': 'Number'}
        question = Question.objects.create(**data)
        response = self.client.post('/questions/%s/delete/' % question.id, {})
        self.assertRedirects(response, self.url)
        self.assertRaises(Question.DoesNotExist, Question.objects.get, **data)
        message = "Question was deleted successfully"
        self.assertIn(message, response.cookies['messages'].value)

    def test_does_not_delete_question_when_it_has_answers(self):
        data = {'text': 'B. Number of cases tested',
                'instructions': "Enter the total number of cases",
                'UID': '00001', 'answer_type': 'Number'}
        question = Question.objects.create(**data)
        country = Country.objects.create(name="Peru")
        Answer.objects.create(question=question, country=country, status="Submitted")

        response = self.client.post('/questions/%s/delete/' % question.id, {})
        self.assertRedirects(response, self.url)
        self.failUnless(Question.objects.get(**data))
        message = "Question was not deleted because it has responses"
        self.assertIn(message, response.cookies['messages'].value)


class RegionalQuestionsViewTest(BaseTest):

    def setUp(self):

        self.client = Client()
        self.user, self.country, self.region = self.create_user_with_no_permissions()

        self.questionnaire = Questionnaire.objects.create(name="JRF 2013 Core English", year=2013, region=self.region)
        self.section = Section.objects.create(name="section", questionnaire=self.questionnaire, order=1, region=self.region)
        self.subsection = SubSection.objects.create(title="subsection 1", section=self.section, order=1, region=self.region)
        self.assign('can_edit_questionnaire', self.user)
        self.client.login(username=self.user.username, password='pass')

        self.url = '/questions/'
        self.form_data = {'text': 'How many kids were immunised this year?',
                          'instructions': 'Some instructions',
                          'export_label': 'blah',
                          'answer_type': 'Number'}

    def test_get_regional_questions(self):
        question1 = Question.objects.create(text='Q1', UID='C00003', answer_type='Number', region=self.region)
        question2 = Question.objects.create(text='Q2', UID='C00002', answer_type='Number', region=self.region)
        question3 = Question.objects.create(text='Q3', UID='C00001', answer_type='Number')
        question_group = question1.question_group.create(subsection=self.subsection)
        question_group.question.add(question2, question3)

        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        templates = [template.name for template in response.templates]
        self.assertIn('questions/index.html', templates)
        self.assertIn(question1, response.context['questions'])
        self.assertIn(question2, response.context['questions'])
        self.assertNotIn(question3, response.context['questions'])
        self.assertIsNone(response.context['active_questions'])

    def test_post_create_question_for_region(self):
        self.assertRaises(Question.DoesNotExist, Question.objects.get, **self.form_data)
        response = self.client.post(self.url + 'new/', data=self.form_data)
        self.assertRedirects(response, self.url)
        self.failUnless(Question.objects.get(region=self.user.user_profile.region, **self.form_data))
        self.assertIn("Question successfully created.", response.cookies['messages'].value)

    def test_delete_question(self):
        data = {'text': 'B. Number of cases tested',
                'instructions': "Enter the total number of cases",
                'UID': '00001', 'answer_type': 'Number'}
        question = Question.objects.create(region=self.region, **data)
        response = self.client.post('/questions/%s/delete/' % question.id, {})
        self.assertRedirects(response, self.url)
        self.assertRaises(Question.DoesNotExist, Question.objects.get, **data)
        message = "Question was deleted successfully"
        self.assertIn(message, response.cookies['messages'].value)

    def test_delete_question_question_not_belonging_to_their_region_shows_error(self):
        user_not_in_same_region, country, region = self.create_user_with_no_permissions(username="asian_chic",
                                                                                        country_name="China",
                                                                                        region_name="ASEAN")
        data = {'text': 'B. Number of cases tested',
                'instructions': "Enter the total number of cases",
                'UID': '00001', 'answer_type': 'Number'}
        paho = Region.objects.create(name="paho")
        question = Question.objects.create(region=paho, **data)
        self.assert_permission_required(self.url)
        self.assign('can_edit_questionnaire', user_not_in_same_region)
        self.client.logout()
        self.client.login(username='asian_chic', password='pass')

        url = '/questions/%s/delete/' % question.id
        response = self.client.post(url)

        self.failUnless(Question.objects.filter(id=question.id))
        self.assertRedirects(response, expected_url='/accounts/login/?next=%s' % quote(url))