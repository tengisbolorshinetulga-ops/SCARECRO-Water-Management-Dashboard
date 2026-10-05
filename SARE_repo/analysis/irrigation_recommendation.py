from pymongo import MongoClient 
from dotenv import load_dotenv
from datetime import datetime
import os 
import sys 

def main(): 
    load_dotenv()
    mongo_uri = os.getenv("MONGODB_URI")
    weather_mongo_uri = os.getenv("WEATHER_MONGODB_URI")

    if "MONGODB_URI" not in os.environ:
        raise ValueError ("MONGODB_URI Environment Variable Is Missing") 

    try : 
        client = MongoClient(mongo_uri)
        weather_client = MongoClient(weather_mongo_uri)
        weather_database = weather_client.get_database("SCARECRO")
        weather_collection = weather_database.get_collection("WEATHER_ANALYSIS")
        weather_data = weather_collection.find_one({"location" : "SOAC_Sandpoint"})
        database = client.get_database("SCARECRO")
        collection_et = database.get_collection("ET_summary")
        IRRIGATION_RECOMMENDATION = database.get_collection("IRRIGATION_RECOMMENDATION")
        et_data = collection_et.find_one({"location" : "SOAC Sandpoint"})
        


    except Exception as e : 
        print(f"Connection Failed {e}")
        sys.exit(1)


    score = 0

    # ET conditions — most important factor
    if et_data["longest_streak"] >= 3:
        score += 25
    elif et_data["longest_streak"] >= 1:
        score += 10

    if et_data["last_two_weeks_percentile_comparison_calculation"] > 20:
        score += 15
    elif et_data["last_two_weeks_percentile_comparison_calculation"] > 10:
        score += 10

    # Rainfall conditions — second most important
    if weather_data["total_rain_fall_this_month"] == 0:
        score += 20
    elif weather_data["total_rain_fall_this_month"] < 1:
        score += 10

    if weather_data["this_week_total_rain_fall"] == 0:
        score += 10

    # Temperature conditions
    if weather_data["days_temp_above_95F"] >= 3:
        score += 10
    elif weather_data["days_temp_above_95F"] >= 1:
        score += 5

    # Humidity — low humidity increases water demand
    if weather_data["humidity_weekly_change_percent"] < -15:
        score += 5

    # Generate recommendation
    if score >= 76:
        recommendation = "High water stress detected — irrigate within 48 hours"
    elif score >= 51:
        recommendation = "Moderate water stress — consider irrigating this week"
    elif score >= 21:
        recommendation = "Mild water stress — monitor conditions closely"
    else:
        recommendation = "Field conditions normal — no irrigation needed"

    print(f"Water Stress Score : {score}/100")
    print(f"Recommendation : {recommendation}")

    irrigation_record  = { 
        "location" : "SOAC SANDPOINT",
        "score" : score,
        "reccomendation" : recommendation,
        "last_updated" : datetime.now()

    }

    IRRIGATION_RECOMMENDATION.update_one(
        {
            "location" : "SOAC SANDPOINT"
        },
        {"$set" : irrigation_record},
        upsert = True
    )

if __name__ == "__main__": 
    main()
    

                                                                




