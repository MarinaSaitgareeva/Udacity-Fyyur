from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ARRAY, ForeignKey, desc
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

db = SQLAlchemy()
# DONE: connect to a local postgresql databas
def db_setup(app):
  app.config.from_object('config')
  db.app = app
  db.init_app(app)
  migrate = Migrate(app, db, render_as_batch=False)
  return db


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  city = Column(String(120))
  state = Column(String(120))
  address = Column(String(120))
  phone = Column(String(120))
  image_link = Column(String(500))
  facebook_link = Column(String(120))

  # DONE: implement any missing fields, as a database migration using Flask-Migrate
  website = Column(String(120))
  genres = Column(ARRAY(String(120)))
  seeking_talent = Column(Boolean, default=False)
  seeking_description = Column(String(120))

  # Venue is the parent (one-to-many) of a Show
  shows = db.relationship('Show', backref='venue', lazy=True)
  # Can reference show.venue (as well as venue.shows)

  def __repr__(self):
    return f'Venue: {self.id}, {self.name}, {self.city}, {self.state}, shows: {self.shows}'

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  genres = Column(ARRAY(String(120)))
  city = Column(String(120))
  state = Column(String(120))
  phone = Column(String(120))
  image_link = Column(String(500))
  facebook_link = Column(String(120))

  # DONE: implement any missing fields, as a database migration using Flask-Migrate
  website = Column(String(120))

  seeking_venue = Column(Boolean, default=False)
  seeking_description = Column(String(120))

  # Artist is the parent (one-to-many) of a Show
  shows = db.relationship('Show', backref='artist', lazy=True)
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