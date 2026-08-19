from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, BooleanField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange


class FeedbackForm(FlaskForm):
    feedback_type = SelectField('Feedback Target', choices=[
        ('Faculty', 'Course Instructor / Faculty Feedback'),
        ('Course', 'Curriculum / Course Syllabus Feedback'),
        ('Institutional', 'College Facilities & Infrastructure Feedback')
    ], default='Faculty')
    
    faculty_id = SelectField('Select Faculty', coerce=int, validators=[Optional()])
    course_id = SelectField('Select Course', coerce=int, validators=[Optional()])
    department_id = SelectField('Select Department', coerce=int, validators=[Optional()])
    
    rating = SelectField('Overall Rating (1 to 5 Stars)', choices=[
        ('5', '⭐⭐⭐⭐⭐ 5 - Excellent'),
        ('4', '⭐⭐⭐⭐ 4 - Very Good'),
        ('3', '⭐⭐⭐ 3 - Good / Average'),
        ('2', '⭐⭐ 2 - Needs Improvement'),
        ('1', '⭐ 1 - Unsatisfactory')
    ], default='5', validators=[DataRequired()])
    
    clarity_rating = SelectField('Subject Clarity & Teaching Quality', choices=[('5','5/5'),('4','4/5'),('3','3/5'),('2','2/5'),('1','1/5')], default='5')
    punctuality_rating = SelectField('Punctuality & Syllabus Coverage', choices=[('5','5/5'),('4','4/5'),('3','3/5'),('2','2/5'),('1','1/5')], default='5')
    helpfulness_rating = SelectField('Doubt Resolution & Guidance', choices=[('5','5/5'),('4','4/5'),('3','3/5'),('2','2/5'),('1','1/5')], default='5')
    
    comments = TextAreaField('Detailed Constructive Feedback & Comments', validators=[DataRequired()])
    is_anonymous = BooleanField('Submit as Anonymous Feedback (Hide my identity)', default=False)
    
    submit = SubmitField('Submit Feedback')
