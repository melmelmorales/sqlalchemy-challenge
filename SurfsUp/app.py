# Import the dependencies
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine using sqlite database file in Resources folder
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

# Create an app, use __name__, and initialize
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Homepage
@app.route("/")
def welcome():
    return (
        f"Welcome to Melissa's Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():
    """Returns the precipitation data for the last year"""
    
    # Calculate the date one year from the most recent date in dataset.
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and precipitation scores
    last_12_months_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in last_12_months_data}

    # Close the session
    session.close()

    return jsonify(precipitation_data)

# Stations route
@app.route('/api/v1.0/stations')
def stations():
    """Returns the list of stations from the dataset"""
    
    # Perform a query to retrieve all stations
    all_stations = session.query(Station.station, Station.name).all()
    
    # Convert query results to a list of dictionaries
    station_list = [{'station': station, 'name': name} for station, name in all_stations]

    # Close the session
    session.close()

    return jsonify(station_list)

# Temperature observations route
@app.route('/api/v1.0/tobs')
def tobs():
    """Returns the date and temperature observations from the most active station over the previous year"""
    
    # Calculate the date one year from the most recent date in dataset.
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    # Perform a query to retrieve the temperature observations for the previous year for the most active station
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a list of dictionaries
    tobs_list = [{'date': date, 'temperature': tobs} for date, tobs in tobs_data]

    # Close the session
    session.close()

    return jsonify(tobs_list)

# Route for temperature data from a start date
@app.route('/api/v1.0/<start>')
def start(start):
    """Returns the minimum, maximum, and average temperature observations from a given start date through the end of the dataset"""
    
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    
    temp_data = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ).filter(Measurement.date >= start_date).all()
    
    # Close the session
    session.close()

    # Create and return a JSON list of the temperature observations 
    temp_observations = {"Tmin": temp_data[0][0], "Tmax": temp_data[0][1], "Tavg": temp_data[0][2]}
    
    return jsonify(temp_observations)

# Route for temperature data between start and end dates
@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    """Returns the minimum, maximum, and average temperature observations between given start and end dates"""
    
    # Define the start and end dates
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    
    temp_range = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    # Close the session
    session.close()

    # Create and return a JSON list of the temperature observations 
    temp_ranges = {"Tmin": temp_range[0][0], "Tmax": temp_range[0][1], "Tavg": temp_range[0][2]}
    
    return jsonify(temp_ranges)

if __name__ == '__main__':
    app.run(debug=True)