#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import desc
from operator import itemgetter
from models import db_setup, Venue, Artist, Show
from datetime import datetime
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# DONE: connect to a local postgresql database
app = Flask(__name__)
moment = Moment(app)
# app.config.from_object('config')
# db = SQLAlchemy(app)
# migrate = Migrate(app, db, render_as_batch=False)
db = db_setup(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# class Venue(db.Model):
#   __tablename__ = 'Venue'

#   id = Column(Integer, primary_key=True)
#   name = Column(String)
#   city = Column(String(120))
#   state = Column(String(120))
#   address = Column(String(120))
#   phone = Column(String(120))
#   image_link = Column(String(500))
#   facebook_link = Column(String(120))

#   # DONE: implement any missing fields, as a database migration using Flask-Migrate
#   website = Column(String(120))
#   genres = Column(ARRAY(String(120)))
#   seeking_talent = Column(Boolean, default=False)
#   seeking_description = Column(String(120))

#   # Venue is the parent (one-to-many) of a Show
#   shows = db.relationship('Show', backref='venue', lazy=True)
#   # Can reference show.venue (as well as venue.shows)

#   def __repr__(self):
#     return f'Venue: {self.id}, {self.name}, {self.city}, {self.state}, shows: {self.shows}'

# class Artist(db.Model):
#   __tablename__ = 'Artist'

#   id = Column(Integer, primary_key=True)
#   name = Column(String)
#   genres = Column(ARRAY(String(120)))
#   city = Column(String(120))
#   state = Column(String(120))
#   phone = Column(String(120))
#   image_link = Column(String(500))
#   facebook_link = Column(String(120))

#   # DONE: implement any missing fields, as a database migration using Flask-Migrate
#   website = Column(String(120))

#   seeking_venue = Column(Boolean, default=False)
#   seeking_description = Column(String(120))

#   # Artist is the parent (one-to-many) of a Show
#   shows = db.relationship('Show', backref='artist', lazy=True)
#   # Can reference show.artist (as well as artist.shows)

#   def __repr__(self):
#     return f'Artist: {self.id}, {self.name}, {self.city}, {self.state}, shows: {self.shows}'

# # DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# class Show(db.Model):
#   __tablename__ = 'Show'

#   id = Column(Integer, primary_key=True)
#   start_time = Column(DateTime, nullable=False, default=datetime.utcnow)

#   artist_id = Column(Integer, ForeignKey('Artist.id'), nullable=False)
#   venue_id = Column(Integer, ForeignKey('Venue.id'), nullable=False)

#   def __repr__(self):
#     return f'Show {self.id} {self.start_time} artist_id={artist_id} venue_id={venue_id}'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
    format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
    format='EE MM, dd, y h:mma'
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  # Create variables to store lists of 10 recent artists and venues 
  recent_artists = []
  recent_venues = []
  # Get 10 recent artists and 10 venues from the database (fyyur).
  artists_data = Artist.query.order_by(desc(Artist.id)).limit(10).all()
  venues_data = Venue.query.order_by(desc(Venue.id)).limit(10).all()
  # Iterate over artists' and venues' data from the database and add it to the created lists.
  for artist in artists_data:
    recent_artists.append({'id': artist.id, 'name': artist.name})
  for venue in venues_data:
    recent_venues.append({'id': venue.id, 'name': venue.name})

  return render_template('pages/home.html', artists=recent_artists, venues=recent_venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  # Create a variable with the current time.
  current_time = datetime.now()
  # Create variable to store all venues from the database (fyuur) order by venue's name.
  venues = Venue.query.order_by(Venue.name).all()
  # Create a variable to store list of dictionaries with city, state, and venues (id, name and num_upcoming_shows).
  data = []
  # Create a variable to store a list of tuples with unique locations for all venues: state + city.
  locations = []
  # Iterate over each venues from the database (fyyur) to add state + city to the locations list.
  for venue in venues:
    locations.append((venue.state, venue.city))
  # Get only unique tuples from list using set() + list()
  # set() method is used to convert any of the iterable to sequence of iterable elements with distinct elements, commonly called Set.
  # list() function takes any iterable as a parameter and returns a list.
  locations = list(set(locations))
  # Sorts list of locations by state, then by city using operator: itemgetter.
  locations.sort(key=itemgetter(0,1))
  # Iterate over unique locations (state and city) to add a dictionary for each venue with id, name and num_upcoming_shows.
  for location in locations:
    venues_list = []
    # Iterate over all venues from the database to add them to the venues_list based on the location (state + city).
    for venue in venues:
      # For each location, see if there are any venues there, and add if so.
      if (venue.state == location[0] and venue.city == location[1]):
        shows_in_venue = Show.query.filter_by(venue_id=venue.id).all()
        # If we've got a venue to add, check how many upcoming shows it has.
        num_upcoming_shows = 0
        for show in shows_in_venue:
          if show.start_time > current_time:
            num_upcoming_shows += 1
        # Add result in the venue_list.
        venues_list.append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': num_upcoming_shows
        })
    # After all venues are added to the list for a given location, add it to the data list.
    data.append({
      'city': location[1],
      'state': location[0],
      'venues': venues_list
    })

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # Create a variable to store user input data from venue's search form.
  search_term = request.form.get('search_term', '')
  # Create variable to store search result from the database (fyyur) based on the user input data from venue's search form.
  search_result = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  # Create a variable to store a list of venues from search result.
  venue_list = []
  # Iterate over each venue in search result and add then in venue list.
  for venue in search_result:
    venue_list.append({
      'id': venue.id,
      'name': venue.name
    })
  # Crate a variable to store a dictionary of venues' number and venues' details (id and name) from search result.
  response = {
    'count': len(search_result),
    'data': venue_list
  }

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id

  # Create a variable to store the selected venue.
  venue = Venue.query.get(venue_id)
  # Check if there is the selected venue in the database (fyyur). If not, redirect to venues page, otherwise open page for the selected venue.
  if not venue:
    return redirect(url_for('venues'))
  else:
    # Create a variable with the current time.
    current_time = datetime.now()
    # Get a list of shows for the selected venue (past_shows and upcoming_shows), and count them.
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    for show in venue.shows:
      if show.start_time > current_time:
        upcoming_shows_count += 1
        upcoming_shows.append({
          'artist_id': show.artist_id,
          'artist_name': show.artist.name,
          'artist_image_link': show.artist.image_link,
          'start_time': str(show.start_time)
        })
      else:
        past_shows_count += 1
        past_shows.append({
          'artist_id': show.artist_id,
          'artist_name': show.artist.name,
          'artist_image_link': show.artist.image_link,
          'start_time': str(show.start_time)
        })
    # Add data for the selected venue.
    data = {
      'id': venue_id,
      'name': venue.name,
      'genres': venue.genres,
      'address': venue.address,
      'city': venue.city,
      'state': venue.state,
      'phone': venue.phone,
      'website': venue.website,
      'facebook_link': venue.facebook_link,
      'seeking_talent': venue.seeking_talent,
      'seeking_description': venue.seeking_description,
      'image_link': venue.image_link,
      'past_shows': past_shows,
      'past_shows_count': past_shows_count,
      'upcoming_shows': upcoming_shows,
      'upcoming_shows_count': upcoming_shows_count
    }

  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion

  # Create a variable to store venue create form.
  form = VenueForm(request.form)
  # Redirect back to form if errors in form validation.
  if form.validate():
    try:
      # Create the new venue with all details.
      new_venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        website=form.website_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
      )
      # on successful db insert, flash success
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + form.name.data + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
      print(sys.exc_info())
      return redirect(url_for('create_venue_submission'))
    finally:
      db.session.close()
      return redirect(url_for('venues'))
  else:
    flash('Error in filling form')
    flash(form.errors)
   
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    # return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # Create variable to store the selected venue.
  venue = Venue.query.get(venue_id)
  venue_name = venue.name
  # Check if there is the selected venue in the database (fyyur). If not, redirect to venues page, if so continue to delete this venue.
  if not venue:
    # User somehow faked this call, redirect venues page.
    return redirect(url_for('venues'))
  else:
    error_on_delete = False
    try:
      db.session.delete(venue)
      db.session.commit()
      flash('Venue(' + venue_name + ') has been deleted successfully!')
    except:
      error_on_delete = True
      flash('Something went wrong, Venue(' + venue_name + ') could not be deleted.')
      db.session.rollback()
    finally:
      db.session.close()
    if error_on_delete:
      flash('An error occurred deleting Venue(' + venue_name + ')')
      abort(500)
    else:
      return jsonify({
        'deleted': True,
        'url': url_for('index')
        })

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return None


#  Update
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # DONE: populate form with values from venue with ID <venue_id>

  # Create a variable to store venue's data from the database (fyyur).
  venue = Venue.query.get(venue_id)
  # Check if there is the selected venue in the database (fyyur). If not, redirect to venues page, otherwise open page for the selected venue.
  if not venue:
    return redirect(url_for('venues'))
  else:
    # Prepopulate the form with the selected venue's data.
    form = VenueForm(obj=venue)
    venue = {
      'id': venue.id,
      'name': venue.name,
      'genres': venue.genres,
      'address': venue.address,
      'city': venue.city,
      'state': venue.state,
      'phone': venue.phone,
      'website': venue.website,
      'facebook_link': venue.facebook_link,
      'seeking_talent': venue.seeking_talent,
      'seeking_description': venue.seeking_description,
      'image_link': venue.image_link
    }

  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(request.form)
  # Check if the Venue Form is valid. If not, redirect to edit_venue_submission page, otherwise updated data for the selected venue.
  if form.validate():
    try:
      # Create variable to store selected venue.
      venue = Venue.query.get(venue_id)
      # Update properties for the selected venue.
      venue.name = form.name.data
      venue.genres = form.genres.data
      venue.address = form.address.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.website = form.website_link.data
      venue.facebook_link = form.facebook_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      venue.image_link = form.image_link.data
      db.session.commit()
      flash('Venue ' + form.name.data + ' was updated successfully!' )
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
      abort(500)
    finally:
      db.session.close()
  else:
    flash(form.errors)
    return redirect(url_for('edit_venue_submission', venue_id=venue_id))

  return redirect(url_for('show_venue', venue_id=venue_id))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database

  # Create a variable to store all artists from the database (fyyur) order by artist's name.
  artists = Artist.query.order_by(Artist.name).all()
  # Create a variable to store list of dictionaries with id and name for each artists from the database (fyyur).
  data = []
  # Iterate over each artists from the database (fyyur) to add them in our data list.
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })

  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  # Create a variable to store user input data from artist's search form.
  search_term = request.form.get('search_term', '')
  # Create variable to store search result from the database (fyyur) based on the user input data from artist's search form.
  search_result = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  # Create a variable to store a list of artists from search result.
  artist_list = []
  # Iterate over each artist in search result and add then in artist list.
  for artist in search_result:
    artist_list.append({
      'id': artist.id,
      'name': artist.name
    })
  # Crate a variable to store a dictionary of artists' number and artists' details (id and name) from search result.
  response = {
    'count': len(search_result),
    'data': artist_list
  }

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # DONE: replace with real artist data from the artist table, using artist_id

  # Create a variable to store the selected artist.
  artist = Artist.query.get(artist_id)
  # Check if there is the selected artist in the database (fyyur). If not, redirect to artists page, otherwise open page for the selected artist.
  if not artist:
    return redirect(url_for('artists'))
  else:
    # Create a variable with the current time.
    current_time = datetime.now()
    # Get a list of shows for the selected artists (past_shows and upcoming_shows), and count them.
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    for show in artist.shows:
      if show.start_time > current_time:
        upcoming_shows_count += 1
        upcoming_shows.append({
          'venue_id': show.venue_id,
          'venue_name': show.venue.name,
          'venue_image_link': show.venue.image_link,
          'start_time': str(show.start_time)
        })
      else:
        past_shows_count += 1
        past_shows.append({
          'venue_id': show.venue_id,
          'venue_name': show.venue.name,
          'venue_image_link': show.venue.image_link,
          'start_time': str(show.start_time)
        })
    # Add data for the selected artist.
    data = {
      'id': artist_id,
      'name': artist.name,
      'genres': artist.genres,
      'city': artist.city,
      'state': artist.state,
      'phone': artist.phone,
      'website': artist.website,
      'facebook_link': artist.facebook_link,
      'seeking_venue': artist.seeking_venue,
      'seeking_description': artist.seeking_description,
      'image_link': artist.image_link,
      'past_shows': past_shows,
      'past_shows_count': past_shows_count,
      'upcoming_shows': upcoming_shows,
      'upcoming_shows_count': upcoming_shows_count
    }

  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion

  # Create a variable to store artist create form.
  form = ArtistForm(request.form)
  # Redirect back to form if errors in form validation.
  if form.validate():
    try:
      # Create the new artist with all details.
      new_artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        website=form.website_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data
      )
      # on successful db insert, flash success
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + form.name.data + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + form.name.data + 'could not be listed.')
      print(sys.exc_info())
      return redirect(url_for('create_artist_submission'))
    finally:
      db.session.close()
      return redirect(url_for('artists'))
  else:
    flash('Error in filling form')
    flash(form.errors)

  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  # return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
   # Create variable to store the selected artist.
  artist = Artist.query.get(artist_id)
  artist_name = artist.name
  # Check if there is the selected artist in the database (fyyur). If not, redirect to artists page, if so continue to delete this artist.
  if not artist:
    # User somehow faked this call, redirect artists page.
    return redirect(url_for('artists'))
  else:
    error_on_delete = False
    try:
      db.session.delete(artist)
      db.session.commit()
      flash('Artist(' + artist_name + ') has been deleted successfully!')
    except:
      error_on_delete = True
      flash('Something went wrong, Artist(' + artist_name + ') could not be deleted.')
      db.session.rollback()
    finally:
      db.session.close()
    if error_on_delete:
      flash('An error occurred deleting Artist(' + artist_name + ')')
      abort(500)
    else:
      return jsonify({
        'deleted': True,
        'url': url_for('index')
      })


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # DONE: populate form with fields from artist with ID <artist_id>

  # Create a variable to store artist's data from the database (fyyur).
  artist = Artist.query.get(artist_id)
  # Check if there is the selected artist in the database (fyyur). If not, redirect to artists page, otherwise open page for the selected artist.
  if not artist:
    return redirect(url_for('artists'))
  else:
    # Prepopulate the form with the selected artist's data.
    form = ArtistForm(obj=artist)
    artist = {
      'id': artist.id,
      'name': artist.name,
      'genres': artist.genres,
      'city': artist.city,
      'state': artist.state,
      'phone': artist.phone,
      'website': artist.website,
      'facebook_link': artist.facebook_link,
      'seeking_venue': artist.seeking_venue,
      'seeking_description': artist.seeking_description,
      'image_link': artist.image_link
    }

  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)
  # Check if the Artist Form is valid. If not, redirect to edit_artist_submission page, otherwise updated data for the selected artist.
  if form.validate():
    try:
      # Create variable to store selected artist.
      artist = Artist.query.get(artist_id)
      # Update properties for the selected artist.
      artist.name = form.name.data
      artist.genres = form.genres.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.website = form.website_link.data
      artist.facebook_link = form.facebook_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      artist.image_link = form.image_link.data
      db.session.commit()
      flash('Artist ' + form.name.data + ' was updated successfully!' )
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + form.name.data + ' could not be updated.')
      abort(500)
    finally:
      db.session.close()
  else:
    flash(form.errors)
    return redirect(url_for('edit_artist_submission', artist_id=artist_id))
  
  return redirect(url_for('show_artist', artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.

  # Create a variable to store all shows from the database (fyyur) order by start time(desc).
  shows = Show.query.order_by(db.desc(Show.start_time))
  # Create a variable to store list of dictionaries with  details for each shows.
  data = []
  # Iterate over each show from the database (fyyur) to add them in our data list.
  for show in shows:
    data.append({
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': str(show.start_time)
    })

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead

  # Create a variable to store show create form.
  form = ShowForm(request.form)
  try:
    # Create the new show with all details.
    new_show = Show(
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      start_time=form.start_time.data
    )
    # on successful db insert, flash success
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
    return redirect(url_for('create_show_submission'))
  finally:
    db.session.close()
    return redirect(url_for('shows'))

  # return render_template('pages/home.html')

  
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
