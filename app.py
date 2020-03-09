#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import abort, Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
import datetime

## Adding Flask migrate
from flask_migrate import Migrate
from sqlalchemy import func, desc

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


# Complete: connect to a local postgresql database
## Ran  - flask db init
## then - flask db migrate
## and  - flask db upgrade
## to create the first migration


migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#show = db.Table('Show',
#    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
#    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
#    db.Column('start_time', db.DateTime, nullable=False)
#)

# Reference for relationship https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html

## Change to support Many to Many with extra fields
## In this case "start_time"
class Show(db.Model):
    __tablename__ = 'Show'
    artist_id = db.Column( db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    venue_id = db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    start_time = db.Column('start_time', db.DateTime, nullable=False)
    artists = db.relationship('Artist', backref='artists')
    venues = db.relationship('Venue', backref='venues')



class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  ## New fields
  genres = db.Column(db.String(120))
  website = db.Column(db.String(2048))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(200))
  ## Relationship
  shows = db.relationship('Show', backref=db.backref('venue', lazy=True), )

    # (Complete) implement any missing fields, as a database migration using Flask-Migrate
    # Fields completed
    # (Complete): add relationships

## Complete: Shows will be a Many-To-Many relationship

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500), default='https://www.ochch.org/wp-content/themes/mast/images/xempty-photo.jpg.pagespeed.ic.rb5Znw4o9F.jpg')
  facebook_link = db.Column(db.String(120))
  ## New fields
  website = db.Column(db.String(2048))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(500))
  shows = db.relationship('Show', backref='artist')
  albums = db.relationship('Album', backref='artitst')

    # (Complete) implement any missing fields, as a database migration using Flask-Migrate
    # Added new fields

# (Complete) Implement Show and Artist models, and complete all model relationships and properties, as a database migration. 

## Album
class Album(db.Model):
  __tablename__ = 'Album'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(50))
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  songs = db.relationship('Song', backref='album')

## Songs
class Song(db.Model):
  __tablename__ = 'Song'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(120))
  track = db.Column(db.Integer, nullable=False)
  album_id = db.Column(db.Integer, db.ForeignKey('Album.id'))




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Completed: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]

  # This parameter will be used in the query. This way I can use the same variable for the "Select" part and 
  # the "Order by" part. 
  countField = func.count(Venue.city)

  # The query will get City, State and the count in descending order so the UI can show Cities with more venues at the top
  # SELECT city, state, count(city) as countField
  # FROM Venue 
  # GROUP BY city, state 
  # ORDER BY countField
  cities = db.session.query(Venue.city, Venue.state, countField).group_by(Venue.city, Venue.state).order_by(desc(countField)).all()
  cityInfo = {}
  prev = ''
  for city in cities:
    cityInfo = {
        "city": city.city,
        "state": city.state,
        "venues" :[]
      }

    # Query the Venue table to get all the venues from each city
    venues = Venue.query.filter(Venue.city==city.city, Venue.state == city.state).all()
    for venue in venues:
      cityInfo['venues'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": 1
          })
    data.append(cityInfo)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Complete: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  newResponse = {
    "count":0,
    "data": []
  }

  # This function will query the Venue table using insensitive Like operator for the name field. 
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form.get('search_term', '')))).all()
  newResponse['count'] = len(venues)

  for venue in venues:
    newResponse['data'].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(venue.shows),
    })
    
  return render_template('pages/search_venues.html', results=newResponse, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # Complete: replace with real venue data from the venues table, using venue_id
  # Complete: add the past and future events

  #### DB connection
  venue = Venue.query.get(venue_id)

  # If no Venue exists with the specified id, the user is returned a 404 error
  if venue == None:
    abort(404, description="Venue not found")

  # Construct the response from the Venue information
  newData = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0
  }

  currentDate = datetime.datetime.now()
  # Fill out the upcoming_shows and past_shows by looping the Shows field (This is a relationship)
  # And adding the show to the respective category

  for show in venue.shows:
    if(show.start_time >= currentDate):
      newData['upcoming_shows'].append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      })
      newData["upcoming_shows_count"] = newData["upcoming_shows_count"] + 1
    else:
      newData['past_shows'].append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      })
      newData["past_shows_count"] = newData["past_shows_count"] + 1

  return render_template('pages/show_venue.html', venue=newData)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Complete: insert form data as a new Venue record in the db, instead
  # Complete (I think): modify data to be the data object returned from db insertion
  # Complete: add values for seeking talent, image link
  form = VenueForm()

  # Validations
  if not form.validate():
    # For each error in the Form, a new flash will be added
    for error in form.errors:
      flash(form.errors[error][0])

    # If the validation fails, the UI will refresh with the same information it already contained
    # This is to avoid having the user fill out the form again
    return render_template('forms/new_venue.html', form=form)

  # Saving the Venue in the database
  try: 
    newVenue =Venue(
      name = form.name.data ,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      genres =form.genres.data, 
      website = form.website.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data)

    db.session.add(newVenue)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
    # completed: on unsuccessful db insert, flash an error instead.
    flash('Something went wrong when adding the venue ' + request.form['name'], 'error')
  finally:
    db.session.close()

  
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Complete: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = {}
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Something went wrong when deleting the venue ' + venue.name, 'error')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # Challenge complete  
  # Complete: check why doesn't redirect
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Complete: replace with real data returned from querying the database

  newData =[]
  artists = Artist.query.all()
  for artist in artists:
    newData.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=newData)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Complete: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".


  newResponse = {
    "count":0,
    "data": []
  }
  # This function will query the Artist table using insensitive Like operator for the name field. 
  artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form.get('search_term', '')))).all()

  newResponse['count'] = len(artists)
  for artist in artists:
    newResponse['data'].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(artist.shows),
    })

  return render_template('pages/search_artists.html', results=newResponse, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist (venue) page with the given artist_id (venue_id)
  # Complete: replace with real artist (venue) data from the artists (venues) table, using artist_id (venue_id)
  # Complete: add the past and future shows

  artist = Artist.query.get(artist_id)

  # If the query doesn't return a value, it means the id doesn't exist
  # The user will get a 404 error
  if artist == None:
    abort(404, description="Artist not found")

  # The Artist object is contruscted
  newData = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
    "albums":[]

  }

  currentDate = datetime.datetime.now()

  # Similar to Venues, the upcoming_shows and past_shows are populated by looping
  # and comparing against the current date.
  for show in artist.shows:
    if(show.start_time >= currentDate):
      newData['upcoming_shows'].append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      })
      newData["upcoming_shows_count"] = newData["upcoming_shows_count"] + 1
    else:
      newData['past_shows'].append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      })
      newData["past_shows_count"] = newData["past_shows_count"] + 1


  # Albums
  for album in artist.albums:
    albumData = {
      "title": album.title,
      "songs": []
    }
    print('Album: ', album.title)
    for song in album.songs:
      albumData["songs"].append({
        "track": song.track,
        "title": song.title
      })
      print('\tTack: ',song.track, ' Title: ', song.title)
    newData["albums"].append(albumData)


  return render_template('pages/show_artist.html', artist=newData)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # Complete: populate form with fields from artist with ID <artist_id>

  #### DB connection

  # If the Id doesn't exist, the user will get a 404 error
  artist = Artist.query.get(artist_id)
  if artist == None:
    abort(404, description="Artist not found")
  
  # When editing an Artist, the UI will show the current data
  newArtist = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }

  form.seeking_description.data = artist.seeking_description
  form.genres.data = artist.genres.split(',')
  form.state.data = artist.state
  return render_template('forms/edit_artist.html', form=form, artist=newArtist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # Complete: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  
  # Validations
  if not form.validate():
    # For each error in the Form, a new flash will be added
    for error in form.errors:
      flash(form.errors[error][0])

    # If the validation fails, the UI will refresh with the same information it already contained
    # This is to avoid having the user fill out the form again
    return redirect(url_for('edit_artist', artist_id=artist_id))

  
  # This is an edit, so it should modify the value already existing in the database. 
  artist = Artist.query.get(artist_id) 
  try:
    artist.name = form.name.data 
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.genres = ','.join(form.genres.data)
    artist.website = form.website.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    db.session.commit()
    flash('Artist ' + form.name.data + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Something went wrong when updating the artist ' + artist.name, 'error')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # Complete: populate form with values from venue with ID <venue_id>
  # Complete: check how to select the genres in the ui
  
  #### DB connection
  venue = Venue.query.get(venue_id)
  if venue == None:
    abort(404, description="Venue not found")

  newData = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  form.seeking_description.data = venue.seeking_description
  form.genres.data = venue.genres.split(',')
  form.state.data = venue.state
  return render_template('forms/edit_venue.html', form=form, venue=newData)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # Completed: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  # Complete: add values for seeking talent, image link
  form = VenueForm()

  # Validations
  if not form.validate():
    # For each error in the Form, a new flash will be added
    for error in form.errors:
      flash(form.errors[error][0])

    # If the validation fails, the UI will refresh with the same information it already contained
    # This is to avoid having the user fill out the form again
    return redirect(url_for('edit_venue', venue_id=venue_id))

  # To edit, it needs to modify the Venue that exists in the DB
  venue = Venue.query.get(venue_id)

  try:
    venue.name = form.name.data 
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.genres = ','.join(form.genres.data)
    venue.website = form.website.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Something went wrong when updating the venue ' + venue.name, 'error')
  finally:
    db.session.close()


  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # Complete: insert form data as a new Artist record in the db, instead
  # Complete (not clear the ask here): modify data to be the data object returned from db insertion
  form = ArtistForm()

  # Validations
  if not form.validate():
    # For each error in the Form, a new flash will be added
    for error in form.errors:
      flash(form.errors[error][0])

    # If the validation fails, the UI will refresh with the same information it already contained
    # This is to avoid having the user fill out the form again
    return render_template('forms/new_artist.html', form=form)
  

  try:
    artist = Artist(
      name = form.name.data, 
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      genres = ','.join(form.genres.data),
      website = form.website.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Something went wrong when listing the artist ' + request.form['name'], 'error')
  finally:
    db.session.close()
  
  # Complete: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # Complete: replace with real venues data.
  # Complete: num_shows should be aggregated based on number of upcoming shows per venue.

  ## From Shows, I'm getting the venues grouping by artist in order to organize in descending order
  countField =  func.count(Show.artist_id)
  venues = db.session.query(Show.venue_id, countField).group_by(Show.venue_id).order_by(desc(countField)).all()

  newShows = []
  for venue in venues:
    # Then I'm getting the actual venue and then the related shows 
    venue = Venue.query.get(venue.venue_id)

    for show in venue.shows:
      newShows.append({
        "venue_id": show.venues.id,
        "venue_name": show.venues.name,
        "artist_id": show.artists.id,
        "artist_name": show.artists.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      })
  return render_template('pages/shows.html', shows=newShows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # Complete: insert form data as a new Show record in the db, instead



  form = ShowForm()
  # Validations
  if not form.validate():
    # For each error in the Form, a new flash will be added
    for error in form.errors:
      flash(form.errors[error][0])

    # If the validation fails, the UI will refresh with the same information it already contained
    # This is to avoid having the user fill out the form again
    return render_template('forms/new_show.html', form=form)

    #Parent
  artist = Artist.query.get(form.artist_id.data)
  if artist == None:
      flash('Invalid Artist ID')

    #Chils
  venue = Venue.query.get(form.venue_id.data)
  if venue == None:
    flash('Invalid Venue ID')

  if artist == None or venue == None:
    return render_template('forms/new_show.html', form=form)

  try:
   
    #Assoc
    s = Show(start_time = form.start_time.data)
    s.venue = venue
    s.artist = artist
    
    db.session.add(s)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('There was an error creating the show :(')
  finally:
    db.session.close()

  
  # Complete: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', description=error), 404

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
