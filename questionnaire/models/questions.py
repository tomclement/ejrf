from django.db import models
from questionnaire.models.base import BaseModel


class Question(BaseModel):

    ANSWER_TYPES = (
        ("Date", "Date"),
        ("MultiChoice", "MultiChoice"),
        ("Number", "Number"),
        ("Text", "Text"),
    )

    text = models.TextField(blank=False, null=False)
    instructions = models.TextField(blank=False, null=True)
    short_instruction = models.CharField(max_length=250, blank=False, null=True)
    UID = models.CharField(blank=False, null=False, max_length=6, unique=True)
    answer_type = models.CharField(blank=False, null=False, max_length=20, choices=ANSWER_TYPES)
    is_core = models.BooleanField(blank=False, null=False)
    is_primary = models.BooleanField(blank=False, null=False)

    def all_answers(self):
        return self.answers.filter(status='Submitted').order_by('answergroup__id').select_subclasses()

    def __unicode__(self):
        return "%s" % self.text

    def group(self):
        return self.question_group.all()[0]

    def is_first_in_group(self):
        questions = self.group().ordered_questions()
        return self == questions[0]

    def is_last_in_group(self):
        questions = self.group().ordered_questions()
        return self == questions[-1]

    def has_question_option_instructions(self):
        return self.options.exclude(instructions=None)


class QuestionOption(BaseModel):
    text = models.CharField(max_length=100, blank=False, null=False)
    question = models.ForeignKey(Question, related_name="options")
    instructions = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return "%s" % self.text