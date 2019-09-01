import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/EnterStartDateYYYYMMDD<br/>"
        f"/api/v1.0/EnterStartDateYYYYMMDD/EnterEndDateYYYYMMDD"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all the dates and precipitation scores"""
    # query to retrieve the data and precipitation scores
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).all()

    # Convert list of tuples into normal list
    precip_scores = list(np.ravel(results))

    return jsonify(precip_scores)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    # Query all stations
    session = Session(engine)
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Latitude"] = latitude
        station_dict["Longitude"] = longitude
        station_dict["Elevation"] = elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of tobs."""
    # Query for the dates and temperature observations from a year from the last data point.
    session = Session(engine)
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_prior = dt.datetime.strptime(max_date.date, '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > year_prior).\
    order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of all_passengers
    yp_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        yp_tobs.append(tobs_dict)

    return jsonify(yp_tobs)

#app to get temp averages from start date entered
@app.route("/api/v1.0/<start>")
def start (start):
    session = Session(engine)

    from_start_date = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    from_start_date_list=list(from_start_date)
    return jsonify(from_start_date_list)

#app to get temp averages between start and end date
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    date_span = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    date_span_list=list(date_span)
    return jsonify(date_span_list)



if __name__ == '__main__':
    app.run(debug=True)