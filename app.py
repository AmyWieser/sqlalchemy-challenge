import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date/<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for all dates and precipitation data
    prcp_data = session.query(Measurement.date, Measurement.prcp)

    session.close()

    # Convert list to a dictionary
    prcp_dict = {}
    for date, prcp in prcp_data:
        prcp_dict[date] = prcp

    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for station data
    station_data = session.query(Station.id, Station.station, Station.name).all()

    session.close()

    # create list of stations 
    station_list = []

    for station in station_data:
        station_dict = {}

        station_dict["id"] = station[0]
        station_dict["station"] = station[1]
        station_dict["name"] = station[2]

        station_list.append(station_dict)

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for dates and temperature for the most active station
    # Find station most active
    station_most_active = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    # Query to find most recent date and 365 days prior and convert into date format
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = (dt.datetime.strptime(last_date, "%Y-%m-%d")).date()

    year_before_last_date = last_date - dt.timedelta(days=365)

    # Query to find temperature for most active station between last date and year before last date
    most_active_temp = session.query(Measurement.date, Measurement.tobs).\
                              filter((Measurement.station == station_most_active)\
                                     & (Measurement.date >= year_before_last_date)\
                                     & (Measurement.date <= last_date)).all()

    session.close()
    
    return jsonify(most_active_temp)

@app.route("/api/v1.0/<start_date>")
def Start_date(start_date):
    # Create list with Min temp, Avg temp & Max temp for a given start date
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for Min temp, Avg temp & Max temptemperature for the start date
    start_stats = session.query(func.min(Measurement.date), func.min(Measurement.tobs),\
        func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    
    start_stats_list = {"Start Date": start_stats[0][0], "Minimum Temp": start_stats[0][1],\
        "Maximum Temp": start_stats[0][3], "Average Temp": start_stats[0][2]}
    session.close()
     
    return jsonify(start_stats_list)

    
if __name__ == "__main__":
    app.run(debug=True)


    