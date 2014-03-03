from django.core.urlresolvers import reverse
from questionnaire.models import Questionnaire, Question
from questionnaire.models.base import BaseModel
from django.db import models


class Section(BaseModel):
    name = models.CharField(max_length=100, blank=False, null=True)
    title = models.CharField(max_length=256, blank=False, null=False)
    order = models.IntegerField(blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    questionnaire = models.ForeignKey(Questionnaire, blank=False, null=False, related_name="sections")

    def ordered_questions(self):
        subsections = self.sub_sections.order_by('order')
        questions = []
        for subsection in subsections:
            for group in subsection.question_group.order_by('order'):
                orders = group.orders.order_by('order')
                questions.extend([group_question_order.question for group_question_order in orders])
        return questions

    def question_orders(self):
        subsections = self.sub_sections.order_by('order')
        _orders = []
        for subsection in subsections:
            for group in subsection.question_group.order_by('order'):
                orders = self._get_orders_in(group)
                _orders.extend(orders)
        return _orders

    def _get_orders_in(self, group):
        orders = group.orders.order_by('order')
        if group.primary_question() and group.grid:
            return self._set_orders_for_grid_questions(group, orders)
        return orders

    @staticmethod
    def _set_orders_for_grid_questions(group, orders):
        _orders = []
        number_of_primary_question_options = group.primary_question()[0].options.all().count()
        for i in range(0, number_of_primary_question_options):
            _orders.extend(orders)
        return _orders

    class Meta:
        ordering = ('order',)
        app_label = 'questionnaire'

    def has_at_least_two_subsections(self):
        return self.sub_sections.count() > 1

    def get_absolute_url(self):
        args = self.questionnaire.id, self.id
        return reverse('questionnaire_entry_page', args=args)

    @classmethod
    def get_next_order(cls, questionnaire):
        sections = cls.objects.filter(questionnaire=questionnaire).reverse()
        return sections[0].order + 1 if sections else 0


class SubSection(BaseModel):
    title = models.CharField(max_length=256, blank=False, null=False)
    order = models.IntegerField(blank=False, null=False)
    section = models.ForeignKey(Section, blank=False, null=False, related_name="sub_sections")
    description = models.TextField(blank=True, null=True)

    def all_question_groups(self):
        return self.question_group.all()

    def all_questions(self):
        all_questions = []
        for question_group in self.all_question_groups():
            all_questions.extend(question_group.all_questions())
        return all_questions

    def parent_question_groups(self):
        return self.question_group.filter(parent=None).exclude(question=None)

    class Meta:
        ordering = ('order',)
        app_label = 'questionnaire'

    def has_at_least_two_groups(self):
        return self.parent_question_groups().count() > 1

    @classmethod
    def get_next_order(cls, section_id):
        subsections = cls.objects.filter(section__id=section_id)
        if subsections.exists():
            return subsections.latest('order').order + 1
        return 0