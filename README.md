# sqlalchemy-challenge
**Instructions**
Congratulations! You've decided to treat yourself to a long holiday vacation in Honolulu, Hawaii. To help with your trip planning, you decide to do a climate analysis about the area. The following sections outline the steps that you need to take to accomplish this task.

**Precipitation Analysis**

![Preciptation](https://user-images.githubusercontent.com/112193116/203108144-6325e18f-9b16-4a70-8790-d4c92f2479cb.png)

**Station Analysis**

The graph presented below,shows the most frequent temperature data of the most frequent station USC00519281 

![Temperarture_Hist](https://user-images.githubusercontent.com/112193116/203108164-6cb689df-6b5f-4e14-b18d-84a86dde8ea4.png)

**Design Your Climate App**

Now that you’ve completed your initial analysis, you’ll design a Flask API based on the queries that you just developed. To do so, use Flask to create your routes as follows:

* Precipitation data

    Route: /api/v1.0/precipitation

    Info.: Daily precipitation data between January 2010 to August 2017

* Station information

    Route: /api/v1.0/stations

    Info.: Station ID and name and othe location details

* Tobs for most active station

    Route: /api/v1.0/tobs

    Info.: Temperature observations

* API data from specific start date

    Route: /api/v1.0/start=

    Info: Minimum, Maximum and Average temperature between start date to the last date of dataset

* API data from specific start and end date

    Route: /api/v1.0/start=/end=

    Info: Minimum, Maximum and Average temperature between start and end date specified in API route

  Note: The date format will be YYYY-MM-DD, i.e. 2016-08-23.
