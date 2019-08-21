import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Date Definitions for Precipitation & Temperature
last_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
latest_date = list(np.ravel(last_date))[0]

# reformat date as date, same as with jupyter content
latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
latest_year = int(dt.datetime.strftime(latest_date, '%Y'))
latest_month = int(dt.datetime.strftime(latest_date, '%m'))
latest_day = int(dt.datetime.strftime(latest_date, '%d'))

#calculate date range
year_prior = dt.date(latest_year, latest_month, latest_day) - dt.timedelta(days=365)
year_prior = dt.datetime.strftime(year_prior, '%Y-%m-%d')

#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Surf's up: Hawaii Climate Analysis<br/>"
        f"Available Routes:<br/><br/>"
        f"Station listing:<br/>"
        f"/api/v1.0/station<br/><br/>"
        f"Precipitation Data:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"Temperature Readings:<br/>"
        f"/api/v1.0/temperature<br/><br/>"
        f"Data since Defined Date (yyyy-mm-dd):<br/>"
        f"/api/v1.0/datesearch/<StartDate><br/><br/>"
        f"Data in a defined Date Range (yyyy-mm-dd)/(yyyy-mm-dd):<br/>"
        f"/api/v1.0/datesearch/<StartDate>/<EndDate>"
    )

@app.route("/api/v1.0/station")
def stations():
    #basic list of stations
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/precipitation")
def precipitation():
    #define columns for precipitation, use calculations from above to define range
    inches = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > year_prior)
                      .order_by(Measurement.date)
                      .all())
    #create list, loop & append date range & precipitation
    precip_data = []
    for INCH in inches:
        precip_dict = {INCH.date: INCH.prcp, "Station": INCH.station}
        precip_data.append(precip_dict)

    return jsonify(precip_data)

@app.route("/api/v1.0/temperature")
def temperature():
#define columns for temperature, use calculations from above to define range
    farenheit = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > year_prior)
                      .order_by(Measurement.date)
                      .all())
#create list, loop & append date range & precipitation
    temp_data = []
    for temp in farenheit:
        temp_dict = {temp.date: temp.tobs, "Station": temp.station}
        temp_data.append(temp_dict)

    return jsonify(temp_data)
       
@app.route("/api/v1.0/datesearch/<StartDate>")
def start(StartDate):
    #call table columns
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    #query data based on date range (formatted date, just like python file)                  
    temp_date =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= StartDate)
                       .group_by(Measurement.date)
                       .all())
    #create a list, loop & append the columns for the date range defined from the JSON requst above
        dates = []
    for time in temp_date:
        date_dict = {}
        date_dict["Date"] = time[0]
        date_dict["Low"] = time[1]
        date_dict["Avg"] = time[2]
        date_dict["High"] = time[3]
        dates.append(date_dict)

    return jsonify(temp_date)

@app.route("/api/v1.0/datesearch/<StartDate>/<EndDate>")
def start_end(StartDate,EndDate):
    #call table columns
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
     #query data based on date range (formatted data, just like python file)                 
    temp_date_range =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= StartDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= EndDate)
                       .group_by(Measurement.date)
                       .all())
    #create a list, loop & append the columns for the date range defined in the JSON request
    dates = []
    for time_range in temp_date_range:
        date_dict = {}
        date_dict["Date"] = time_range[0]
        date_dict["Low"] = time_range[1]
        date_dict["Avg"] = time_range[2]
        date_dict["High"] = time_range[3]
        dates.append(date_dict)

    return jsonify(temp_date_range)

if __name__ == '__main__':
    app.run(debug=True, port=5009)
