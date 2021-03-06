import itertools


class AnswerTypes(object):
    NUMBER = "Number"
    INTEGER = "Integer"
    DECIMAL = "Decimal"
    MULTIPLE_RESPONSE = "MultipleResponse"
    MULTI_CHOICE = "MultiChoice"
    DATE = "Date"

    VALID_TYPES = {
        DATE: [
            "DD/MM/YYYY",
            "MM/YYYY"
        ],
        MULTI_CHOICE: [],
        MULTIPLE_RESPONSE: [],
        NUMBER: [
            DECIMAL,
            INTEGER
        ],
        "Text": []
    }

    @classmethod
    def has_subtype(cls, answer_type):
        return len(cls.VALID_TYPES[answer_type]) > 0

    @classmethod
    def is_valid_sub_type(cls, answer_type, answer_sub_type):
        return cls.VALID_TYPES[answer_type].__contains__(answer_sub_type)

    @classmethod
    def answer_types(cls):
        return tuple(map(lambda (k, v): (k, k), cls.VALID_TYPES.iteritems()))

    @classmethod
    def answer_sub_types(cls):
        subtypes = filter(None, [v for (k, v) in cls.VALID_TYPES.iteritems()])
        return tuple(map(lambda v: (v, v), itertools.chain(*subtypes)))

    @classmethod
    def is_mutlichoice_or_multiple(cls, answer_type):
        return answer_type == cls.MULTI_CHOICE or answer_type == cls.MULTIPLE_RESPONSE

    @classmethod
    def is_integer(cls, answer_type):
        return answer_type == cls.INTEGER
