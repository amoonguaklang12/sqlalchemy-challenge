from flask import Flask, jsonify

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Find the most recent date in the data set.
most_recent_date = session.query(func.max(Measurement.date))\
    .first()[0]

# Calculate the date one year from the last date in data set.
year_before_recent = '2016-08-23'

# Perform a query to retrieve the data and precipitation scores
year_in_review = session.query(Measurement.date, Measurement.prcp)\
    .filter(Measurement.date.between(year_before_recent, most_recent_date))\
    .all()

# Dictionary of precipitation data
precipitation_dict = {}
count = 0
for record in year_in_review:
    precipitation_dict[year_in_review[count][0]] = year_in_review[count][1]
    count += 1

#Station Data Query
station_data = session.query(Station.station, Station.name).all()

#Dictionary of station data
station_dict = {}
count = 0
for station in station_data:
    station_dict[station_data[count][0]] = station_data[count][1]
    count += 1

#Query for most active station
most_active_station = most_active_stations = session.query(Measurement.station, func.count(Measurement.station))\
    .group_by(Measurement.station)\
    .order_by(func.count(Measurement.station).desc())\
    .all()[0][0]

#Query for dates and temperature observations of the most-active station for the previous year
active_station_year_in_review = session.query(Measurement.date, Measurement.tobs)\
    .filter(Measurement.date.between(year_before_recent, most_recent_date))\
    .filter(Measurement.station == most_active_station)\
    .all()

#Dictionary of temperature for the previous year of the most active station
active_station_temp_dict = {}
count = 0
for temp in active_station_year_in_review:
    active_station_temp_dict[active_station_year_in_review[count][0]] = active_station_year_in_review[count][1]
    count += 1
    
#Query for a specified temperature range

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def homepage():
    return (
        f"Welcome to the homepage!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"You can enter a specific START date, as well as an END date to pull temperature data for that range:<br/>"
        f"/api/v1.0/temp/2017-08-01<br/>"
        f"/api/v1.0/temp/2017-08-01/2017-08-23<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return precipitation data for the last year as json"""
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def station():
    """Return station data as json"""
    
    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def temperature():
    """Return temperature data for the last year as json"""
    
    return jsonify(active_station_temp_dict)

@app.route("/api/v1.0/temp", methods=['get'])
def temp():
    start  = request.args.get('start', None)
    end  = request.args.get('end', None)
    """Return min, max, and average temperature data for the specified date range as json"""
    
    desc_dict = {}
    #if there is no end date specified
    if end == None:
        min_temp = session.query(Measurement.date, func.min(Measurement.tobs))\
            .filter(Measurement.date >= start)\
            .first()

        max_temp = session.query(Measurement.date, func.max(Measurement.tobs))\
            .filter(Measurement.date >= start)\
            .first()

        avg_temp = session.query(Measurement.date, func.avg(Measurement.tobs))\
            .filter(Measurement.date >= start)\
            .first()
        
        #building the dict
        desc_dict["Min Temp"] = min_temp[1]
        desc_dict["Max Temp"] = max_temp[1]
        desc_dict["Avg Temp"] = round(avg_temp[1], 1)
        
        return jsonify(desc_dict)
   
    #if there is an end date specified
    else:
        min_temp = session.query(Measurement.date, func.min(Measurement.tobs))\
            .filter(Measurement.date.between(start, end))\
            .first()

        max_temp = session.query(Measurement.date, func.max(Measurement.tobs))\
            .filter(Measurement.date.between(start, end))\
            .first()

        avg_temp = session.query(Measurement.date, func.avg(Measurement.tobs))\
            .filter(Measurement.date.between(start, end))\
            .first()
        
        #building the dict
        desc_dict["Min Temp"] = min_temp[1]
        desc_dict["Max Temp"] = max_temp[1]
        desc_dict["Avg Temp"] = round(avg_temp[1], 1)
    
        return jsonify(desc_dict)

if __name__ == "__main__":
    app.run(debug=True, use_reloader = False)