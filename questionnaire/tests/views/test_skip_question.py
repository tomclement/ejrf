from questionnaire.tests.base_test import BaseTest
from django.test import Client
from questionnaire.models import Question, SkipQuestion, QuestionOption, Questionnaire, Section, SubSection, QuestionGroup
import json


class SkipQuestionPostTest(BaseTest):
    def setUp(self):
        self.client = Client()
        self.url = "/questionnaire/subsection/skiprules/"
        user = self.create_user(group=self.GLOBAL_ADMIN, org="WHO")
        self.assign('can_edit_questionnaire', user)
        self.client.login(username=user.username, password='pass')
        region = None

        questionnaire = Questionnaire.objects.create(name="JRF 2013 Core English", year=2013, region=region)

        section = Section.objects.create(name="section", questionnaire=questionnaire, order=1)

        subsection = SubSection.objects.create(title="subsection 1", section=section, order=1)
        subsection2 = SubSection.objects.create(title="subsection 2", section=section, order=1)
        subsection3 = SubSection.objects.create(title="subsection 2", section=section, order=1)
        self.subsection_id = subsection.pk
        question_group = QuestionGroup.objects.create(subsection_id=subsection.id)

        root_question = Question.objects.create(text='Q1', UID='C00003', answer_type='MultiChoice', region=region)
        skip_question = Question.objects.create(text='Q2', UID='C00004', answer_type='Number', region=region)
        self.random_question = Question.objects.create(text='Q3', UID='C00005', answer_type='Number', region=region)

        question_group.question.add(root_question)
        question_group.question.add(skip_question)
        question_group.question.add(self.random_question)

        self.subsection_with_only_root_question = subsection3.pk
        question_group2 = QuestionGroup.objects.create(subsection_id=self.subsection_with_only_root_question)
        question_group2.question.add(root_question)

        self.subsection_with_only_skip_question = subsection2.pk
        question_group3 = QuestionGroup.objects.create(subsection_id=self.subsection_with_only_skip_question)
        question_group3.question.add(skip_question)

        response = QuestionOption.objects.create(text="Some response", question=root_question, UID="U0003")
        self.form_data = {'root-question': str(root_question.pk),
                          'responses': str(response.pk),
                          'skip-question': str(skip_question.pk),
                          'subsection-id': str(self.subsection_id)}

    def test_post_skip_question(self):
        self.assertEqual(SkipQuestion.objects.all().count(), 0)
        response = self.client.post(self.url, data=self.form_data)
        self.assertEqual(201, response.status_code)
        self.assertEqual(SkipQuestion.objects.all().count(), 1)

    def test_post_skip_question_for_root_question_not_existing(self):
        self.assertEqual(SkipQuestion.objects.all().count(), 0)
        data = self.form_data
        data['root-question'] = '341543'
        response = self.client.post(self.url, data=data)
        self.assertEqual(400, response.status_code)
        self.assertEqual(json.loads(response.content)['result'], 'root-question does not exist')
        self.assertEqual(SkipQuestion.objects.all().count(), 0) 

    def test_post_skip_question_for_response_not_existing(self):
        self.assertEqual(SkipQuestion.objects.all().count(), 0) 
        data = self.form_data
        data['responses'] = '341543'
        response = self.client.post(self.url, data=data)
        self.assertEqual(400, response.status_code)
        self.assertEqual(json.loads(response.content)['result'], 'response does not exist')
        self.assertEqual(SkipQuestion.objects.all().count(), 0)

    def test_post_skip_question_for_skip_question_not_existing(self):
        self.assertEqual(SkipQuestion.objects.all().count(), 0)
        data = self.form_data
        data['skip-question'] = '341543'
        response = self.client.post(self.url, data=data)
        self.assertEqual(400, response.status_code)
        self.assertEqual(json.loads(response.content)['result'], 'skip-question does not exist')
        self.assertEqual(SkipQuestion.objects.all().count(), 0)

    def test_post_skip_question_for_root_question_not_being_part_of_subsection(self):
        self.assertEqual(SkipQuestion.objects.all().count(), 0)
        data = self.form_data
        data['subsection-id'] = self.subsection_with_only_skip_question
        response = self.client.post(self.url, data=self.form_data)
        self.assertEqual(400, response.status_code)
        self.assertEqual(json.loads(response.content)['result'], 'root-question is not part of subsection')
        self.assertEqual(SkipQuestion.objects.all().count(), 0)

    def test_post_skip_question_for_skip_question_not_being_part_of_subsection(self):
        self.assertEqual(SkipQuestion.objects.all().count(), 0)
        data = self.form_data
        data['subsection-id'] = self.subsection_with_only_root_question
        response = self.client.post(self.url, data=self.form_data)
        self.assertEqual(400, response.status_code)
        self.assertEqual(json.loads(response.content)['result'], 'skip-question is not part of subsection')
        self.assertEqual(SkipQuestion.objects.all().count(), 0)

    def test_post_skip_question_for_response_one_of_root_questions_options(self):
        self.assertEqual(SkipQuestion.objects.all().count(), 0)
        data = self.form_data
        data['root-question'] = self.random_question.pk
        response = self.client.post(self.url, data=data)
        self.assertEqual(400, response.status_code)
        self.assertEqual(json.loads(response.content)['result'],
                         "root question's options does not contain the provided response")
        self.assertEqual(SkipQuestion.objects.all().count(), 0)

    def test_post_skip_question_root_question_is_not_equal_to_skip_question(self):
        self.assertEqual(SkipQuestion.objects.all().count(), 0)
        data = self.form_data
        data['skip-question'] = data['root-question']
        response = self.client.post(self.url, data=data)
        self.assertEqual(400, response.status_code)
        self.assertEqual(json.loads(response.content)['result'], "root question cannot be the same as skip question")
        self.assertEqual(SkipQuestion.objects.all().count(), 0)

class SkipQuestionGetTest(BaseTest):
    def setUp(self):
        self.client = Client()
        self.url = "/questionnaire/subsection/skiprules/"
        user = self.create_user(group=self.GLOBAL_ADMIN, org="WHO")
        self.assign('can_edit_questionnaire', user)
        self.client.login(username=user.username, password='pass')
        region = None

        questionnaire = Questionnaire.objects.create(name="JRF 2013 Core English", year=2013, region=region)

        section = Section.objects.create(name="section", questionnaire=questionnaire, order=1)

        subsection = SubSection.objects.create(title="subsection 1", section=section, order=1)

        question_group = QuestionGroup.objects.create(subsection_id=subsection.id)
        
        root_question = Question.objects.create(text='Q1', UID='C00003', answer_type='MultiChoice', region=region)
        skip_question = Question.objects.create(text='Q2', UID='C00004', answer_type='Number', region=region)
        question_group.question.add(root_question)
        question_group.question.add(skip_question)

        response = QuestionOption.objects.create(text="Some response", question=root_question, UID="U0003")

    def test_get_skip_questions_when_questions_exists(self):
        print "hello"
        # response = self.client.get("/")