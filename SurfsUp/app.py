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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
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



if __name__ == '__main__':
    app.run(debug=True)
