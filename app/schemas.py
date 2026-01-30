from .extensions import ma
from .models import User, Question, Option, Trivia, TriviaParticipation, UserAnswer
from marshmallow import fields

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)

class OptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Option
        load_instance = True
        include_fk = True

class QuestionSchema(ma.SQLAlchemyAutoSchema):
    options = ma.Nested(OptionSchema, many=True)
    difficulty = fields.Method("get_difficulty_name")

    class Meta:
        model = Question
        load_instance = True

    def get_difficulty_name(self, obj):
        return obj.difficulty.name

class TriviaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Trivia
        load_instance = True

class TriviaDetailSchema(TriviaSchema):
    questions = ma.Nested(QuestionSchema, many=True) # This might need adjustment as it is M2M via TriviaQuestion

class RankingSchema(ma.Schema):
    user = fields.String(attribute='user.name')
    score = fields.Integer()
    completed = fields.Boolean()
