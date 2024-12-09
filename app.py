import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Set up the database engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database into ORM classes
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

# Initialize Flask app
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Welcome to the Hawaii Climate Analysis API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of precipitation data."""
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)


    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    session.close()

    precip = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precip)

if __name__ == "__main__":
    app.run(debug=True)



@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of all stations."""
    results = session.query(Station.station).all()


    session.close()


    stations = list(np.ravel(results))

    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return a JSON list of temperature observations for the previous year."""
  
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps=temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """
    Return the minimum, average, and maximum temperatures for a given start or start-end date range.
    """


    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]


    if not end:
      
        start = dt.datetime.strptime(start, "%m%d%Y").date()

        results = session.query(*sel).filter(Measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify({
            "start_date": start.strftime("%Y-%m-%d"),
            "temperature_stats": temps
        })

    start = dt.datetime.strptime(start, "%m%d%Y").date()
    end = dt.datetime.strptime(end, "%m%d%Y").date()

    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    temps = list(np.ravel(results))

    return jsonify({
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "temperature_stats": temps
    })


if __name__ == "__main__":
    app.run(debug=True)

