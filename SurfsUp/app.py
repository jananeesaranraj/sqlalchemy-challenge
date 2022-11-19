import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
import datetime as dt
import numpy as np
from flask import Flask,jsonify


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
@app.route("/")
def Welcome():
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
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    recent_date = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precip_data=session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= query_date).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    precipitation_list = []
    for date,prcp in precip_data:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precipitation_list.append(precip_dict)
    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    stations = session.query(Station.station).all()
    session.close()
    # Convert list of tuples into normal list
    station_names = list(np.ravel(stations))
    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    active_station = session.query(Measurement.station,func.count(Measurement.station)).\
           group_by(Measurement.station).\
           order_by(func.count(Measurement.station).desc()).first()
    station=active_station.station
    temp_data=session.query(Measurement.tobs).filter(Measurement.station == station).\
                                     filter(Measurement.date >= query_date).all()
    session.close()

    temp_list =list(np.ravel(temp_data))
    return jsonify(temp_list)

@app.route("/api/v1.0/start=<start>")
def start_date(start):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    min_temp =session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).scalar()
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).scalar()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).scalar()
    session.close()
    if min_temp is None:
            return jsonify({"error": "Start date not found."}), 404
    temp_dict={}
    temp_dict["TMIN"] = min_temp
    temp_dict["TMAX"] = max_temp
    temp_dict["TAVG"] = avg_temp
    return jsonify(temp_dict)

@app.route("/api/v1.0/start=<start>/end=<end>")
def start_end(start,end):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    min_temp =session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).\
              filter(Measurement.date <= end).scalar()
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).\
              filter(Measurement.date <= end).scalar()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).\
               filter(Measurement.date <= end).scalar()
    session.close()
    if min_temp is None:
            return jsonify({"error": "Start date not found."}), 404
    temp_dict={}
    temp_dict["TMIN"] = min_temp
    temp_dict["TMAX"] = max_temp
    temp_dict["TAVG"] = avg_temp
    return jsonify(temp_dict)


if __name__ == '__main__':
    app.run(debug=True)
