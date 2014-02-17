from django.forms import ModelForm
from django import forms
from questionnaire.models import Question


class QuestionForm(ModelForm):

    class Meta:
        model = Question
        fields = ['text', 'instructions', 'short_instruction', 'answer_type']
        widgets = {'instructions':  forms.Textarea(attrs={"rows": 6, "cols": 50}),
                   'short_instruction':  forms.Textarea(attrs={"rows": 2, "cols": 50})}

    def save(self, commit=True):
        question = super(QuestionForm, self).save(commit)
        question.UID = Question.next_uid()
        if commit:
            question.save()
        return super(QuestionForm, self).save(commit)