from django.utils.datastructures import SortedDict

from questionnaire.models import Answer, AnswerGroup
from questionnaire.services.questionnaire_entry_form_service import QuestionnaireEntryFormService


class UserQuestionnaireService(object):
    def __init__(self, country, questionnaire, version=None):
        self.version = version
        self.country = country
        self.questionnaire = questionnaire
        self.answers_in_questionnaire = self.questionnaire_answers()
        self.current_answer_status = Answer.DRAFT_STATUS
        self.set_versions()
        self.answers = self.answers_in_questionnaire.filter(version=self.POST_version)
        self.edit_after_submit = not self.POST_version == self.GET_version

    def all_answers(self):
        return Answer.objects.filter(country=self.country).select_subclasses()

    def questionnaire_answers(self):
        answer_groups = AnswerGroup.objects.filter(
            grouped_question__subsection__section__questionnaire=self.questionnaire)
        answers = Answer.objects.filter(country=self.country, answergroup__in=answer_groups,
                                        questionnaire=self.questionnaire).select_subclasses()
        if self.version:
            return answers.filter(version=self.version)
        return answers

    def submit(self):
        for answer in self.answers:
            answer.status = Answer.SUBMITTED_STATUS
            answer.save()
        self.questionnaire.submissions.create(country=self.country, version=self.version or self.GET_version)

    def answer_version(self):
        answers = self.answers_in_questionnaire
        if not answers.exists():
            return 1

        draft_answers = answers.filter(status=Answer.DRAFT_STATUS)
        if draft_answers.exists():
            return draft_answers.latest('modified').version

        self.current_answer_status = Answer.SUBMITTED_STATUS
        return answers.latest('modified').version + 1

    def set_versions(self):
        self.POST_version = self.answer_version()
        if self.current_answer_status == Answer.SUBMITTED_STATUS:
            self.GET_version = self.POST_version - 1
        else:
            self.GET_version = self.POST_version

    def required_sections_answered(self):
        for section in self.questionnaire.sections.all():
            if not self.answered_required_questions_in(section):
                self.unanswered_section = section
                return False
        return True

    def answered_required_questions_in(self, section):
        required_question_in_section = filter(lambda question: question.is_required, section.ordered_questions())
        return self.answers.filter(question__in=required_question_in_section).count() == len(
            required_question_in_section)

    def all_sections_questionnaires(self):
        initial = {'country': self.country, 'status': 'Draft', 'version': self.version or self.POST_version,
                   'questionnaire': self.questionnaire}
        questionnaires = SortedDict()
        for section in self.questionnaire.sections.order_by('order'):
            questionnaires[section] = QuestionnaireEntryFormService(section, initial=initial)
        return questionnaires

    def preview(self):
        version = self.version or self.POST_version
        return self.questionnaire.submissions.filter(country=self.country, version=version).exists()

    def attachments(self):
        return self.questionnaire.support_documents.filter(country=self.country)