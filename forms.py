from datetime import datetime
from flask_wtf import FlaskForm as Form
from enums import Genre, State
from wtforms import (
  StringField,
  SelectField,
  SelectMultipleField,
  DateTimeField,
  BooleanField
)
from wtforms.fields.html5 import TelField
from wtforms.validators import (
  DataRequired,
  URL,
  Optional
)
import re


def is_valid_phone(number):
  ''' Validate phone numbers like:
  1234567890 - no space
  123.456.7890 - dot separator
  123-456-7890 - dash separator
  123 456 7890 - space separator

  Patterns:
  000 = [0-9]{3}
  0000 = [0-9]{4}
  -.  = ?[-. ]

  Note: (? = optional) - Learn more: https://regex101.com/
  '''
  regex = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
  return regex.match(number)

class ShowForm(Form):
  artist_id = StringField(
    'artist_id',
    validators=[DataRequired()]
  )
  venue_id = StringField(
    'venue_id',
    validators=[DataRequired()]
  )
  start_time = DateTimeField(
    'start_time',
    validators=[DataRequired()],
    default= datetime.today()
  )

class VenueForm(Form):
  name = StringField(
    'name',
    validators=[DataRequired()]
  )
  city = StringField(
    'city',
    validators=[DataRequired()]
  )
  state = SelectField(
    'state', 
    validators=[DataRequired()],
    choices=State.choices()
  )
  address = StringField(
    'address',
    validators=[DataRequired()]
  )
  phone = TelField(
    'phone',
    validators=[DataRequired()]
  )
  image_link = StringField(
    'image_link',
    validators=[Optional(), URL()]
  )
  genres = SelectMultipleField(
    # DONE implement enum restriction
    'genres',
    validators=[DataRequired()],
    choices=Genre.choices()
  )
  facebook_link = StringField(
    'facebook_link',
    validators=[Optional(), URL()]
  )
  website_link = StringField(
    'website_link',
    validators=[Optional(), URL()]
  )
  seeking_talent = BooleanField( 
    'seeking_talent',
    validators=[Optional()]
  )
  seeking_description = StringField(
    'seeking_description',
    validators=[Optional()]
  )
  def validate(self):
    '''Define a custom validate method in your Form:'''
    rv = Form.validate(self)
    if not rv:
      return False
    if not is_valid_phone(self.phone.data):
      self.phone.errors.append('Invalid phone.')
      return False
    if not set(self.genres.data).issubset(dict(Genre.choices()).keys()):
      self.genres.errors.append('Invalid genres.')
      return False
    if self.state.data not in dict(State.choices()).keys():
      self.state.errors.append('Invalid state.')
      return False
    # if pass validation
    return True


class ArtistForm(Form):
  name = StringField(
    'name',
    validators=[DataRequired()]
  )
  city = StringField(
    'city',
    validators=[DataRequired()]
  )
  state = SelectField(
    'state',
    validators=[DataRequired()],
    choices=State.choices()
  )
  phone = TelField(
    'phone',
    validators=[DataRequired()]
  )
  image_link = StringField(
    'image_link',
    validators=[Optional(), URL()]
  )
  genres = SelectMultipleField(
    'genres',
    validators=[DataRequired()],
    choices=Genre.choices()
  )
  facebook_link = StringField(
    # DONE implement enum restriction
    'facebook_link',
    validators=[Optional(), URL()]
  )
  website_link = StringField(
    'website_link',
    validators=[Optional(), URL()]
  )
  seeking_venue = BooleanField( 
    'seeking_venue',
    validators=[Optional()],
  )
  seeking_description = StringField(
    'seeking_description',
    validators=[Optional()]
  )
  def validate(self):
    '''Define a custom validate method in your Form:'''
    rv = Form.validate(self)
    if not rv:
      return False
    if not is_valid_phone(self.phone.data):
      self.phone.errors.append('Invalid phone.')
      return False
    if not set(self.genres.data).issubset(dict(Genre.choices()).keys()):
      self.genres.errors.append('Invalid genres.')
      return False
    if self.state.data not in dict(State.choices()).keys():
      self.state.errors.append('Invalid state.')
      return False
    # if pass validation
    return True