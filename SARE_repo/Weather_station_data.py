import requests
import os 
import time
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient


def main(): 
    load_dotenv()
    api_key = os.getenv("AMBIENT_API_KEY")
    app_key = os.getenv("AMBIENT_APPLICATION_KEY")
    mongo_uri = os.getenv("MONGODB_URI")

 

    if not api_key : 
        raise ValueError("AMBIENT_API_KEY missing in enviroment variable")
    if not app_key : 
        raise ValueError(":AMBIENT_APPLICATION_KEY missing in enviroment variable")
    if not mongo_uri : 
        raise ValueError("MONGODB_URI missing in enviroment variable")
    


    client = MongoClient(mongo_uri)

    try :
        client.admin.command('ping')
        print("Connected to MongoDB!")
    except Exception as e: 
        print(f"Failed: {e}")


  
    database = client["SCARECRO"]
    weather_station = database["WEATHER_STATION"]
    air_quality_collection = database["AIR_QUALITY"]
    leaf_collection = database["LEAF_WETNESS"]


    response = requests.get(
    url="https://rt.ambientweather.net/v1/devices",
    params={
        "applicationKey": app_key,
        "apiKey": api_key,
    }
)
    
    time.sleep(1)
    print(response.status_code)
    data = response.json()
    df = pd.DataFrame(data)
    df_last = pd.DataFrame([data[0]["lastData"]])
    print(df_last)

    record = data[0]["lastData"]
    record["macAddress"] = data[0]["macAddress"]

    leaf_record = { 
        "leafwetness1" : record["leafwetness1"],
        "batt_lw1" : record["batt_lw1"],
        "macAddress" : record["macAddress"],
        "date" : record["date"]
    }

    air_quality_record = { 
        "aqi_pm25" : record["aqi_pm25"],
        "aqi_pm25_24h" : record["aqi_pm25_24h"],
        "pm25" : record["pm25"],
        "pm25_24h" : record["pm25_24h"],
        "batt_25" : record["batt_25"],
        "macAddress" : record["macAddress"],
        "date" : record["date"],
    }
    weather_record = dict(record) 
    weather_record.pop("leafwetness1")
    weather_record.pop("batt_lw1")
    weather_record.pop("pm25")
    weather_record.pop("pm25_24h")
    weather_record.pop("aqi_pm25")
    weather_record.pop("aqi_pm25_24h")
    weather_record.pop("batt_25")
                               

    leaf_collection.update_one(
        {
        
            "macAddress" : record["macAddress"],
            "date" : record["date"],


        },
        {"$set":leaf_record},
        upsert=True
    )

    air_quality_collection.update_one(
        {
            "macAddress" : record["macAddress"],
            "date" : record["date"], 
        },
        {"$set": air_quality_record},
        upsert=True
    )

    weather_station.update_one(
        {
            "macAddress" : record["macAddress"],
            "date" : record["date"],
        },
        {"$set":weather_record}, 
        upsert=True
    )

if __name__ == "__main__":
    main()


