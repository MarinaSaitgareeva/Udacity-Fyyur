#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------

import dateutil.parser
import babel
from flask import (
  Flask,
  render_template,
  request,
  flash,
  redirect,
  url_for)
from flask_moment import Moment
from flask_migrate import Migrate 
import logging
from logging import Formatter, FileHandler
from forms import *
from sqlalchemy import desc
from models import db, Venue, Artist, Show
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# DONE: connect to a local postgresql database
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
# Initiate app.
db.init_app(app)
migrate = Migrate(app, db, render_as_batch=False)


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

  # Create variable to store all venues from the database (fyuur) order by venue's name.
  venues = Venue.query.order_by(Venue.name).all()
  # Create a variable to store list of dictionaries with city, state, and venues (id, name and num_upcoming_shows).
  data = []
  # Create a variable to store a list with unique locations for all venues: state + city.
  locations = Venue.query.distinct(Venue.city, Venue.state).all()
  # Iterate over each location from the created list to add details (city, state, id, name, num_upcoming_shows) for each venue.
  for location in locations:
    data.append({
      'city': location.city,
      'state': location.state,
      'venues': [{
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
      } for venue in venues if
        venue.city == location.city and venue.state == location.state]
    })

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
      'name': venue.name,
      'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
    })
  # Crate a variable to store a dictionary of venues' number and venues' details (id and name) from search result.
  response = {
    'count': len(search_result),
    'data': venue_list
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id

  # Create a variable to store the selected venue (return the object or raise a 404 error if the object is not found).
  venue = Venue.query.get_or_404(venue_id)
  # Get a list of shows for the selected venue (past_shows and upcoming_shows), and count them.
  past_shows = []
  upcoming_shows = []
  for show in venue.shows:
    temp_show = {
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
      past_shows.append(temp_show)
    else:
      upcoming_shows.append(temp_show)
  # Add data for the selected venue (object class to dict).
  # The vars() function returns the __dict__ attribute of an object.
  # The __dict__ attribute is a dictionary containing the object's changeable attributes.
  data = vars(venue)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

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

  # Set the FlaskForm for venue.
  form = VenueForm(request.form, meta={'csrf': False})
  # Validate all fields
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
    except ValueError as e:
      # If there is any error, roll back it
      db.session.rollback()
      print(e)
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    finally:
      db.session.close()
  # If there is any invalid field
  else:
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)
  
  return redirect(url_for('venues'))
   
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    # return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # Create variable to store the selected venue (return the object or raise a 404 error if the object is not found).
  venue = Venue.query.get_or_404(venue_id)
  venue_name = venue.name
  try:
    db.session.delete(venue)
    db.session.commit()
    flash('Venue(' + venue_name + ') has been deleted successfully!')
  except ValueError as e:
    db.session.rollback()
    print(e)
    flash('Something went wrong, Venue (' + venue_name + ') could not be deleted.')
  finally:
    db.session.close()
    
  return redirect(url_for('venues'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return None


#  Update
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # DONE: populate form with values from venue with ID <venue_id>

  # Create a variable to store venue's data from the database (fyyur) (return the object or raise a 404 error if the object is not found).
  venue = Venue.query.get_or_404(venue_id)
  # Prepopulate the form with the selected venue's data.
  form = VenueForm(obj=venue)
  venue = vars(venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(request.form, meta={'csrf': False})
  # Check if the Venue Form is valid. If not, redirect to edit_venue_submission page, otherwise updated data for the selected venue.
  if form.validate():
    try:
      # Create variable to store selected venue (return the object or raise a 404 error if the object is not found).
      venue = Venue.query.get_or_404(venue_id)
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
    except ValueError as e:
      db.session.rollback()
      print(e)
      flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
    finally:
      db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    form = VenueForm(request.form, meta={'csrf': False})
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
      'name': artist.name,
      'num_upcoming_shows': len([show for show in artist.shows if show.start_time > datetime.now()])
    })

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
      'name': artist.name,
      'num_upcoming_shows': len([show for show in artist.shows if show.start_time > datetime.now()])
    })
  # Crate a variable to store a dictionary of artists' number and artists' details (id and name) from search result.
  response = {
    'count': len(search_result),
    'data': artist_list
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # DONE: replace with real artist data from the artist table, using artist_id

  # Create a variable to store the selected artist (return the object or raise a 404 error if the object is not found).
  artist = Artist.query.get_or_404(artist_id)
  # Get a list of shows for the selected artists (past_shows and upcoming_shows), and count them.
  past_shows = []
  upcoming_shows = []
  for show in artist.shows:
    temp_show = {
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
        past_shows.append(temp_show)
    else:
      upcoming_shows.append(temp_show)
  # Add data for the selected artist (object class to dict).
  # The vars() function returns the __dict__ attribute of an object.
  # The __dict__ attribute is a dictionary containing the object's changeable attributes.
  data = vars(artist)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

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

  # Set the FlaskForm for artist.
  form = ArtistForm(request.form, meta={'csrf': False})
  # Validate all fields
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
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + form.name.data + ' was successfully listed!')
    except ValueError as e:
      # If there is any error, roll back it
      db.session.rollback()
      print(e)
      flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    finally:
      db.session.close()
  # If there is any invalid field
  else:
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

  return redirect(url_for('artists'))

  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  # return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
   # Create variable to store the selected artist (return the object or raise a 404 error if the object is not found).
  artist = Artist.query.get_or_404(artist_id)
  artist_name = artist.name
  try:
    db.session.delete(artist)
    db.session.commit()
    flash('Artist(' + artist_name + ') has been deleted successfully!')
  except ValueError as e:
    db.session.rollback()
    print(e)
    flash('Something went wrong, Artist (' + artist_name + ') could not be deleted.')
  finally:
    db.session.close()
  
  return redirect(url_for('artists'))


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # DONE: populate form with fields from artist with ID <artist_id>

  # Create a variable to store artist's data from the database (fyyur).
  artist = Artist.query.get(artist_id)
  # Check if there is the selected artist in the database (fyyur). If not, redirect to artists page, otherwise open page for the selected artist.
  # Prepopulate the form with the selected artist's data.
  form = ArtistForm(obj=artist)
  artist = vars(artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form, meta={'csrf': False})
  # Check if the Artist Form is valid. If not, redirect to edit_artist_submission page, otherwise updated data for the selected artist.
  if form.validate():
    try:
      # Create variable to store selected artist (return the object or raise a 404 error if the object is not found).
      artist = Artist.query.get_or_404(artist_id)
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
    except ValueError as e:
      db.session.rollback()
      print(e)
      flash('An error occurred. Artist ' + form.name.data + ' could not be updated.')
    finally:
      db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    form = ArtistForm(request.form, meta={'csrf': False})
    return redirect(url_for('edit_artist_submission', artist_id=artist_id))
  
  return redirect(url_for('show_artist', artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.

  # Create a variable to store all shows from the database (fyyur) order by start time(desc).
  shows = db.session.query(Show).join(Venue).join(Artist).all()
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

  # Set the FlaskForm for venue.
  form = ShowForm(request.form, meta={'csrf': False})
  # Validate all fields
  if form.validate():
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
    except ValueError as e:
      db.session.rollback()
      print(e)
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
  # If there is any invalid field
  else:
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)
    
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
