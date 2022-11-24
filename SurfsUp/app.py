import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
import datetime as dt
import numpy as np
from flask import Flask,jsonify
import pandas as pd

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine,reflect=True)

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
# Home route
@app.route("/")
def Welcome():
# list all the available routes
    return(
        f"<b>Welcome To Honululu Climate API</b><br/>"
        f"{'*'*40}<br/>"
        f"<b>Available Routes:</b><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start=<YYYY-MM-DD><br/>"
        f"/api/v1.0/start=<YYYY-MM-DD>/end=<YYYY-MM-DD><br/>"
        f"{'-'*60}<br/>"
        f"<b>Note:</b><br/>"
        f"1.Route <b>tobs</b> will show only the result of the most active station.<br/>"
        f"2.The <b>date format</b> will be YYYY-MM-DD"
    )

# Precipitation rount
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query precipitation data
    recent_date = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precip_data=session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= query_date).all()
    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    precipitation_list = []
    for date,prcp in precip_data:
        precip_dict = {}
        precip_dict[date] = prcp
        # precip_dict["prcp"] = prcp
        precipitation_list.append(precip_dict)
    return jsonify(precipitation_list)

# Station route
@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

     # Query all stations
    stations = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()

    session.close()

    # Create a dictionary from the row data and append to a list of stations
    station_list=[]
    for station in stations:
        station_dict={}
        station_dict["station"]= station.station
        station_dict["station name"]=station.name
        station_dict["latitude"]=station.latitude
        station_dict["longitude"]=station.longitude
        station_dict["elevation"]=station.elevation
        station_list.append(station_dict)
    return jsonify(station_list)

# TOBS route
@app.route("/api/v1.0/tobs")
def tobs():
     # Create our session (link) from Python to the DB
    session = Session(engine)
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query for the most active active station
    active_station = session.query(Measurement.station,func.count(Measurement.station)).\
           group_by(Measurement.station).\
           order_by(func.count(Measurement.station).desc()).first()
    station=active_station.station
    # Query temp data related to the most active station
    temp_data=session.query(Measurement.tobs).filter(Measurement.station == station).\
                                     filter(Measurement.date >= query_date).all()
    session.close()
     # Convert list of tuples into normal list
    temp_list =list(np.ravel(temp_data))
    return jsonify(temp_list)

# Start Date Route
@app.route("/api/v1.0/start=<start>")
def start_date(start):
     # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the max,min and avg temp from the dataset greater than or equal to the given start date
    results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs))\
        .filter(Measurement.date >= start).all()

    first_date = session.query(Measurement.date).order_by(
        Measurement.date).first()
    last_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()

    session.close()

    # Creat a date list of dataset
    date_list = pd.date_range(start=first_date[0], end=last_date[0])

    # Create a dictionary from the row data and append to a list of temp_data
    temp_data = []
    for tmin, tmax, tavg in results:
        temp_data_dict = {
            'Start Date': start,
            'End Date': last_date[0]
        }
        temp_data_dict['T-MIN'] = tmin
        temp_data_dict['T-MAX'] = tmax
        temp_data_dict['T-AVG'] = tavg
        temp_data.append(temp_data_dict)

        # If statement for date input in API search
        if start in date_list:
            return jsonify(temp_data)
        else:
            return jsonify({
                "error": f"Date: {start} not found. Date must be between {first_date[0]} and {last_date[0]}"
            }), 404

@app.route("/api/v1.0/start=<start>/end=<end>")
def start_end(start,end):
     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the max,min and avg temp from the dataset for the given start and end date range
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    min_temp =session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).\
              filter(Measurement.date <= end).scalar()
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).\
              filter(Measurement.date <= end).scalar()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).\
               filter(Measurement.date <= end).scalar()
    session.close()
    
    # Creat a date list of dataset
    first_date = session.query(Measurement.date).order_by(
        Measurement.date).first()
    last_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()
    
    date_list = pd.date_range(start=first_date[0], end=last_date[0])

    # Create a dictionary from the row data and append to a list of temp details
    temp_dict={}
    temp_dict["Start Date"] = start
    temp_dict["End Date"] = end
    temp_dict["T-MIN"] = min_temp
    temp_dict["T-MAX"] = max_temp
    temp_dict["T-AVG"] = avg_temp
    
    # If statement for date input in API 
    if start and end in date_list:
        if start <= end:
            return jsonify(temp_dict)
        elif start > end:
            return jsonify({
                 "error": f'{start} is greater than {end}'
             })
    else:
            return jsonify({
                "error": f"Date: {start} to {end} not found. Date must be between {first_date[0]} and {last_date[0]}"
            }), 404
# app.run statement
if __name__ == '__main__':
    app.run(debug=True)
