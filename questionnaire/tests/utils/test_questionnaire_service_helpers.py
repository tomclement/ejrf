from questionnaire.tests.base_test import BaseTest
from questionnaire.utils.questionnaire_entry_helpers import extra_rows, clean_list, clean_data_dict


class QuestionnaireServiceHelperTest(BaseTest):
    def test_get_number_of_extra_rows_supplied_for_an_answer_type(self):
        data = {u'MultiChoice-MAX_NUM_FORMS': u'3', u'MultiChoice-TOTAL_FORMS': u'3',
                u'MultiChoice-INITIAL_FORMS': u'3', u'MultiChoice-0-response': [1, '0,1'],
                u'MultiChoice-1-response': [2, '1,1'], u'MultiChoice-2-response': [3, '2,1'],
                u'Number-MAX_NUM_FORMS': u'3', u'Number-TOTAL_FORMS': u'3',
                u'Number-INITIAL_FORMS': u'3', u'Number-0-response': ['22', '0,1'],
                u'Number-1-response': ['44', '1,1'], u'Number-2-response': ['33', '2,1'],
                u'Text-MAX_NUM_FORMS': u'3', u'Text-TOTAL_FORMS': u'3',
                u'Text-INITIAL_FORMS': u'3', u'Text-0-response': ['Haha', '0,1'],
                u'Text-1-response': ['Hehe', '1,1'], u'Text-2-response': ['hehehe', '2,1'],
                u'Date-MAX_NUM_FORMS': u'3', u'Date-TOTAL_FORMS': u'3',
                u'Date-INITIAL_FORMS': u'3', u'Date-0-response': ['2014-2-2', '0,1'],
                u'Date-1-response': ['2014-2-2', '1,1'], u'Date-2-response': ['2014-2-2', '2,1'],
        }

        data = clean_data_dict(dict(data))

        self.assertEqual(['0', '1', '2'], extra_rows(data, 'Number', 1))
        self.assertEqual(['0', '1', '2'], extra_rows(data, 'MultiChoice', 1))
        self.assertEqual(['0', '1', '2'], extra_rows(data, 'Date', 1))
        self.assertEqual(['0', '1', '2'], extra_rows(data, 'Text', 1))

    def test_get_number_of_extra_rows_supplied_for_an_answer_type_when_there_are_more_than_one_grid_of_the_same_type(
            self):
        data = {u'MultiChoice-MAX_NUM_FORMS': u'6', u'MultiChoice-TOTAL_FORMS': u'6',
             u'MultiChoice-INITIAL_FORMS': u'6', u'MultiChoice-0-response': [1, '0,1'],
             u'MultiChoice-1-response': [5, '0,2'], u'MultiChoice-2-response': [2],
             u'MultiChoice-3-response': [2, '1,1'],  u'MultiChoice-4-response': [3, '2,1'],
             u'MultiChoice-5-response': [6, '1,2'],
             u'Number-MAX_NUM_FORMS': u'3', u'Number-TOTAL_FORMS': u'3',
             u'Number-INITIAL_FORMS': u'3', u'Number-0-response': ['22','0,1'],
             u'Number-1-response': ['44','1,1'],  u'Number-2-response': ['33', '2,1'],
             u'Text-MAX_NUM_FORMS': u'6', u'Text-TOTAL_FORMS': u'6',
             u'Text-INITIAL_FORMS': u'6', u'Text-0-response': ['Haha','0,1'],
             u'Text-1-response': ['Hehe1', '0,2'], u'Text-2-response': ['hehe2'],
             u'Text-3-response': ['Hehe','1,1'],  u'Text-4-response': ['hehehe', '2,1'],
             u'Text-5-response': ['Hehe','1,2'],
             u'Date-MAX_NUM_FORMS': u'3', u'Date-TOTAL_FORMS': u'3',
             u'Date-INITIAL_FORMS': u'3', u'Date-0-response': ['2014-2-2', '0,1'],
             u'Date-1-response': ['2014-2-2','1,1'],  u'Date-2-response': ['2014-2-2','2,1'],
             }

        data = clean_data_dict(dict(data))
        self.assertEqual(['0', '1', '2'], extra_rows(data, 'Number', 1))
        self.assertEqual(['0', '1', '2'], extra_rows(data, 'MultiChoice', 1))
        self.assertEqual(['0', '1'], extra_rows(data, 'MultiChoice', 2))
        self.assertEqual(['0', '1', '2'], extra_rows(data, 'Date', 1))
        self.assertEqual(['0', '1', '2'], extra_rows(data, 'Text', 1))
        self.assertEqual(['0', '1'], extra_rows(data, 'Text', 2))

    def test_get_extra_rows_when_type_is_repeated_per_row(self):
        data = {u'Number-1-response': [u'2', u'0,181'], u'MultiChoice-MAX_NUM_FORMS': [u'6'], u'redirect_url': [u''],
                u'save_draft': [u''], u'Number-6-response': [u'7', u'2,181'], u'Number-INITIAL_FORMS': [u'3'],
                u'Number-0-response': [u'1', u'0,181'], u'MultiChoice-0-response': [u'96', u'0,181'],
                u'MultiChoice-1-response': [u'115', u'0,181'], u'Number-5-response': [u'6', u'1,181'],
                u'Number-MAX_NUM_FORMS': [u'9'], u'MultiChoice-4-response': [u'99', u'2,181'],
                u'MultiChoice-TOTAL_FORMS': [u'6'], u'Number-3-response': [u'4', u'1,181'],
                u'Number-TOTAL_FORMS': [u'9'], u'MultiChoice-3-response': [u'116', u'1,181'],
                u'Number-2-response': [u'3', u'0,181'], u'MultiChoice-5-response': [u'117', u'2,181'],
                u'Number-7-response': [u'8', u'2,181'], u'Number-8-response': [u'9', u'2,181'],
                u'csrfmiddlewaretoken': [u'tx2R4QCrpl8IuHfaagFauUtC6XDs3u9C'],
                u'MultiChoice-2-response': [u'98', u'1,181'], u'MultiChoice-INITIAL_FORMS': [u'2'],
                u'Number-4-response': [u'5', u'1,181']}

        data = clean_data_dict(dict(data))
        self.assertEqual(['0', '1', '2'], extra_rows(data, "Number", group_id=181))
        self.assertEqual(['0', '1', '2'], extra_rows(data, "MultiChoice", group_id=181))

    def test_splits_stuff_to_a_valid_list(self):
        self.assertEqual([u'2', u'0',u'181'], clean_list([u'2', u'0,181']))
        self.assertEqual([u'2'], clean_list([u'2']))
        self.assertEqual('2', clean_list('2'))
        self.assertEqual(2, clean_list(2))

    def test_clean_data_dict(self):
        data = {'haha': [u'2', u'0,181'], 'hoho': [u'2', u'0,181']}
        self.assertEqual({'haha':[u'2', u'0', u'181'], 'hoho':[u'2', u'0', u'181']}, clean_data_dict(data))

        string_data = {'haha': u'2'}
        self.assertEqual(string_data, clean_data_dict(string_data))

        int_data = {'haha': 2}
        self.assertEqual(int_data, clean_data_dict(int_data))