from datetime import datetime
from flask_wtf import Form 
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, AnyOf, URL, Length, ValidationError, Regexp
from Enums import StatesEnums, GenreEnums

generesSet = set(GenreEnums.choicesSingle())

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

# This custom validator is for testing/learning custom validators
def leng(max=-1):
    def _leng(form, field):
        if len(field.data)> max:
            raise ValidationError('Field %s must be less than %d characters' % (field.name, max))
    return _leng

# This custom validator is adapted to allow empty strings
# the original URL() would raise an error with empty strings
def myURL():
    def _myURL(form, field):
        # Will remove the URL validator in case the user tries again
        # with an empty URL
        if len(field.validators) >2:
            field.validators.pop()

        if not field.data == "":
            field.validators.append(URL())
    return _myURL

# Custom Validator for Genre. A set was generated using the GenreEnum
# Then looping thorugh all the selected genres in the field, it validates
# against the set. If the set doesn't contain the value
# a validation error is raised. 
def ValidGenre():
    def _ValidGenre(form, field):
        for genre in field.data:
            if not genre in generesSet:
                 raise ValidationError()
    return _ValidGenre

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired(), leng(max=120)]
    )
    city = StringField(
        'city', validators=[DataRequired(), leng(max=120)]
    )
    state = SelectField(
        'state', validators=[DataRequired(),
        AnyOf([choice.value for choice in StatesEnums])
        ],
        choices= StatesEnums.choices()
    )
    address = StringField(
        'address', validators=[DataRequired(), leng(max=120)]
    )
    phone = StringField(
        'phone', validators=[Regexp('^[0-9]\d{2}-\d{3}-\d{4}$',message='Incorrect phone format')]
    )
    image_link = StringField(
        'image_link', validators=[myURL(), leng(max=500)]
    )
    genres = SelectMultipleField(
        # Complete implement enum restriction
        'genres', validators=[DataRequired(), ValidGenre()],
        choices = GenreEnums.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[myURL(), leng(max=120)]
    )
    # new items
    website = StringField(
        'website', validators=[myURL(), leng(max=120)]
    )
    
    seeking_talent =  BooleanField()
    seeking_description = TextAreaField(
        'seeking_description', validators=[leng(max=200)]
    )

# Artis Form
class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired(), leng(max=120)]
    )
    city = StringField(
        'city', validators=[DataRequired(), leng(max=120)]
    )
    state = SelectField(
        'state', validators=[DataRequired(),
        AnyOf([choice.value for choice in StatesEnums])
        ],
        choices= StatesEnums.choices()
    )
    phone = StringField(
        # Complete implement validation logic for phone
        'phone', validators=[Regexp('^[0-9]\d{2}-\d{3}-\d{4}$',message='Incorrect phone format')]
    )
    image_link = StringField(
        'image_link', validators=[myURL(), leng(max=500)]
    )
    genres = SelectMultipleField(
        # Complete implement enum restriction
        'genres', validators=[DataRequired(), ValidGenre()],
        choices = GenreEnums.choices()
    )
    facebook_link = StringField(
        # Complete implement enum restriction
        'facebook_link', validators=[myURL(), leng(max=120)]
    )

    # new items
    website = StringField(
        'website', validators=[myURL(), leng(max=120)]
    )
    
    seeking_venue =  BooleanField()
    seeking_description = TextAreaField(
        'seeking_description', validators=[leng(max=500)]
    )

# Complete IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM


