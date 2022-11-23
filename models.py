from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
  Column,
  String,
  Integer,
  Text,
  DateTime,
  Boolean,
  ARRAY,
  ForeignKey)
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# Initialized without explicit app (Flask instance)
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = Column(Integer, primary_key=True)
  name = Column(String, nullable=False)
  city = Column(String(120), nullable=False)
  state = Column(String(120), nullable=False)
  address = Column(String(120), nullable=False)
  phone = Column(String(120), nullable=False)
  image_link = Column(String(500))
  facebook_link = Column(String(120))

  # DONE: implement any missing fields, as a database migration using Flask-Migrate
  website = Column(String(120))
  genres = Column(ARRAY(String()), nullable=False)
  seeking_talent = Column(Boolean, default=False)
  seeking_description = Column(Text)

  # Venue is the parent (one-to-many) of a Show
  shows = db.relationship(
    'Show',
    backref='venue',
    lazy='joined',
    cascade='all, delete'
  )
  # Can reference show.venue (as well as venue.shows)

  def __repr__(self):
    return f'Venue: {self.id}, {self.name}, {self.city}, {self.state}, shows: {self.shows}'

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = Column(Integer, primary_key=True)
  name = Column(String, nullable=False)
  city = Column(String(120), nullable=False)
  state = Column(String(120), nullable=False)
  phone = Column(String(120), nullable=False)
  image_link = Column(String(500))
  facebook_link = Column(String(120))

  # DONE: implement any missing fields, as a database migration using Flask-Migrate
  website = Column(String(120))
  genres = Column(ARRAY(String()), nullable=False)
  seeking_venue = Column(Boolean, default=False)
  seeking_description = Column(Text)

  # Artist is the parent (one-to-many) of a Show
  shows = db.relationship(
    'Show',
    backref='artist',
    lazy='joined,
    cascade='all, delete'
  )
  # Can reference show.artist (as well as artist.shows)

  def __repr__(self):
    return f'Artist: {self.id}, {self.name}, {self.city}, {self.state}, shows: {self.shows}'

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Show'

  id = Column(Integer, primary_key=True)
  start_time = Column(DateTime, nullable=False, default=datetime.utcnow)

  artist_id = Column(Integer, ForeignKey('Artist.id'), nullable=False)
  venue_id = Column(Integer, ForeignKey('Venue.id'), nullable=False)

  def __repr__(self):
    return f'Show {self.id} {self.start_time} artist_id={self.artist_id} venue_id={self.venue_id}'