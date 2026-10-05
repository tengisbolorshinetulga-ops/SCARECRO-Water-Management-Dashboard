from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd
from datetime import timedelta, datetime
from datetime import timezone
import os
import sys 

def main() : 
    load_dotenv()

    mongo_uri = os.getenv("WEATHER_MONGODB_URI")
  

    if "WEATHER_MONGODB_URI" not in os.environ: 
        raise ValueError ("WEATHER_MONGODB_URI Environment Variable Is Missing")

    try : 
        client = MongoClient(mongo_uri)
        database = client.get_database("SCARECRO")
        collection = database.get_collection("WEATHER_STATION")
        Weather_analysis_collection = database.get_collection("WEATHER_ANALYSIS")
        Weather_trend_collection = database.get_collection("WEATHER_TRENDS")
        df = pd.DataFrame(list(collection.find()))

    except Exception as e :
        print(f"Connection Failed {e}")
        sys.exit(1)


    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= thirty_days_ago]
    df = df.sort_values(by="date")
    df = df.set_index("date")

    daily_average = df["tempf"].resample("D").mean()

    weekly_average = df["tempf"].resample("W").mean()
    #print(f"Weekly Temprature Average : {weekly_average}")

    # Test Run Change It
    days_temp_was_higher_than_95F = daily_average[daily_average > 95]
    print(f"Days Temprature Was Above 95 Degrees : {len(days_temp_was_higher_than_95F)}")

    longest_streak = 0 
    streak_start = None
    streak_end = None

    if len(days_temp_was_higher_than_95F) > 0 :
        print(f"Days Temprature Was Above 95 Degrees In the Last 30 Days:{days_temp_was_higher_than_95F}")

        date_gaps = days_temp_was_higher_than_95F.index.to_series().diff()
        #print(f"date_gaps:{ date_gaps}")
        is_new_streak = date_gaps != pd.Timedelta('1 days')
        #print(f"is_new_streak : {is_new_streak}")
        streak_groups = is_new_streak.cumsum()
        #print(f"streak_groups :{streak_groups}")
        streak_lengths = streak_groups.value_counts()
        #print(f"streak_lengths : {streak_lengths}")
        longest_streak = streak_lengths.max()
        #print(f"longest_streak : {longest_streak}")
        longest_streak_group = streak_lengths.idxmax()
        #print(f"longets_streak_group : {longest_streak_group}")
        date_time_of_longest_streak_group = streak_groups[streak_groups == longest_streak_group]
        #print(date_time_of_longest_streak_group)

    
        streak_start = date_time_of_longest_streak_group.index.min()
        streak_end = date_time_of_longest_streak_group.index.max()
        print(f"Start Date Of The Longest Continuous Streak : {streak_start.strftime('%Y-%m-%d')}")
        print(f"End Date Of The Longest Continuous Streak : {streak_end.strftime('%Y-%m-%d')}")

    else :
        print(f"No Days Exceeded 95F Threshold In The Last 30 Days")


    most_recent_week_average = weekly_average.iloc[-1]
    #print(f"Most Recent Week Average Temp : {most_recent_week_average}")
    second_recent_week_average = weekly_average.iloc[-2]
    #print(f"Second Recent Week Average Temp : {second_recent_week_average}")

    formula_for_last_two_weeks_percentile_change =  ((most_recent_week_average - second_recent_week_average) / second_recent_week_average) * 100
    print(f"Temprature Percentile Change Between The Past 2 Weeks : {round(formula_for_last_two_weeks_percentile_change, 2)}%")

    if formula_for_last_two_weeks_percentile_change > 0 : 
        print(f"Temprature Has Increased {round(formula_for_last_two_weeks_percentile_change, 2)}% This Week")
    else :  
        print(f" Temprature Has Decreased {round(abs(formula_for_last_two_weeks_percentile_change), 2)}% This Week")

    Temp_average_for_past_4_weeks = weekly_average.iloc[-4:]
    print(f"Average Temprature For The Past 4 Weeks : {Temp_average_for_past_4_weeks}")



    # RAIN FALL SCRIPT START

    daily_average_rain_fall = df["dailyrainin"].resample("D").last()
    #print(f"Average Rain Fall From Today : {daily_average_rain_fall}")

    total_rain_fall_this_month = daily_average_rain_fall.sum()
    print(f" Total Rain Fall For This Month : {total_rain_fall_this_month}")

    number_of_days_with_rain_fall_this_month = daily_average_rain_fall[daily_average_rain_fall > 0]
    print(f"Number Of Days With Rainfall This Month : {len(number_of_days_with_rain_fall_this_month)}")

    date_of_last_rain = df["lastRain"].iloc[-1]
    print(f"Date Of The Last Rain : {date_of_last_rain[:10]}")

    total_weekly_rain_fall = df["dailyrainin"].resample("W").sum()
    this_week_total_rain_fall = total_weekly_rain_fall.iloc[-1]
    print(f"Total Rain Fall For The Week : {this_week_total_rain_fall}")
    

    weekly_average_rain_fall = df["dailyrainin"].resample("W").mean()
    most_recent_weekly_average_rain_fall = weekly_average_rain_fall.iloc[-1]
    second_weekly_average_weekly_rainfall = weekly_average_rain_fall.iloc[-2]
    print(f"Most Recent Weekly Average Rain Fall : {most_recent_weekly_average_rain_fall}")

    average_rainall_past_4_weeks = weekly_average_rain_fall.iloc[-4:]
    print(f"Average Rainfall For The Past 4 Weeks : {average_rainall_past_4_weeks}")




    if second_weekly_average_weekly_rainfall == 0 :
        if most_recent_weekly_average_rain_fall > 0 :
            print(f"Rainfall Has Increased This Week")
        else : 
            print(f"No Rainfall Change For The Past 2 Weeks")

    else : 
        recent_two_weeks_rainfall_percentile_difference_formula = ((most_recent_weekly_average_rain_fall - second_weekly_average_weekly_rainfall) / second_weekly_average_weekly_rainfall)* 100
        if recent_two_weeks_rainfall_percentile_difference_formula > 0 :
            print(f"Rainfall Inreased {round(recent_two_weeks_rainfall_percentile_difference_formula,2)}%")
        else : 
            print(f"Rainfall Decreased {round(recent_two_weeks_rainfall_percentile_difference_formula,2)}%")




    # Humidity Script Start


    weekly_average_humidity = df["humidity"].resample("W").mean()
    last_4_weeks_average_humidity = weekly_average_humidity.iloc[-4:]
    print(f"Weekly Average Humidity For The Past 4 Weeks : {last_4_weeks_average_humidity}")

    most_recent_weekly_average_humidity = weekly_average_humidity.iloc[-1]
    second_recent_weekly_average_humidity = weekly_average_humidity.iloc[-2]

    formula_for_last_two_weeks_percentile_change_humidity = ((most_recent_weekly_average_humidity - second_recent_weekly_average_humidity) / second_recent_weekly_average_humidity) * 100
    if most_recent_weekly_average_humidity > second_recent_weekly_average_humidity : 
        print(f"Humidity This Week Was {round(formula_for_last_two_weeks_percentile_change_humidity,2)}% Higher Compared To Last Week")
    else :
        print(f"Humidity This Week Was {round(formula_for_last_two_weeks_percentile_change_humidity,2)}% Lower Compared To Last Week")

    daily_average_humidity = df["humidity"].resample("D").mean()



    number_of_days_with_average_humidity_above_85 = daily_average_humidity[daily_average_humidity > 85]
    print(f"Number Of Days Humidity Exceeded Above 85% : {len(number_of_days_with_average_humidity_above_85)}")

    humidity_longest_streak = 0
    start_date_of_longest_streak_humidity = None 
    end_date_of_longest_streak_group = None

    if len(number_of_days_with_average_humidity_above_85) > 0 :

        humidity_date_gaps = number_of_days_with_average_humidity_above_85.index.to_series().diff()
        humidity_is_new_streak = humidity_date_gaps != pd.Timedelta('1 days')
        humidity_streak_groups = humidity_is_new_streak.cumsum()
        humidity_streak_lengths = humidity_streak_groups.value_counts()
        humidity_longest_streak = humidity_streak_lengths.max()
        humidity_longest_streak_group = humidity_streak_lengths.idxmax()
        date_of_the_longest_streak_group = humidity_streak_groups[humidity_streak_groups == humidity_longest_streak_group]
        start_date_of_longest_streak_humidity = date_of_the_longest_streak_group.index.min()
        end_date_of_longest_streak_group = date_of_the_longest_streak_group.index.max()
        print(f"Start Date Of The Longest Humidity Streak Above 85% : {start_date_of_longest_streak_humidity.strftime('%Y-%m-%d')}")
        print(f"End Date Of The Longest Humidity Streak Above 85% : {end_date_of_longest_streak_group.strftime('%Y-%m-%d')}")

    else : 
        print("No Days Exceeded Above 85% Humidity")


    weather_summary_record = { 
        "days_temp_above_95F" : int(len(days_temp_was_higher_than_95F)),
        "longest_streak" : int(longest_streak),
        "streak_start" : (streak_start),
        "streak_end" : (streak_end),
        "temp_weekly_change_percent": float(round(formula_for_last_two_weeks_percentile_change, 2)),
        "total_rain_fall_this_month" : int(total_rain_fall_this_month),
        "number_of_days_with_rain_fall_this_month" : len(number_of_days_with_rain_fall_this_month),
        "date_of_last_rain" : (date_of_last_rain),
        "this_week_total_rain_fall" : int(this_week_total_rain_fall),
        "most_recent_weekly_average_rain_fall" : float(most_recent_weekly_average_rain_fall),
        "humidity_weekly_change_percent" : float(round(formula_for_last_two_weeks_percentile_change_humidity,2 )),
        "number_of_days_with_average_humidity_above_85" : int(len(number_of_days_with_average_humidity_above_85)),
        "humidity_longest_streak" : int(humidity_longest_streak),
        "start_date_of_longest_streak_humidity" : (start_date_of_longest_streak_humidity), 
        "end_date_of_longest_streak_group" : (end_date_of_longest_streak_group),
        "location" : "SOAC_Sandpoint",
        "last_updated" : datetime.now(),
        "weather_analysis_start_date" : thirty_days_ago
                                                              

        }
    Weather_analysis_collection.update_one( 
        {
            "macAddress" : "54:32:04:41:6A:EC"
        },
        {"$set" : weather_summary_record},
        upsert = True 
    )


    for (week_date, avg_temp), (_, avg_rainfall), (_, avg_humidity) in zip(
        Temp_average_for_past_4_weeks.items(),
        average_rainall_past_4_weeks.items(),
        last_4_weeks_average_humidity.items()
    ):

        weather_trends_record = { 
            "location" : "SOAC_Sandpoint", 
            "date" : week_date, 
            "average temp for the past 4 weeks" : float(avg_temp),
            "average rainfall for the past 4 weeks" : float(avg_rainfall), 
            "average humidity for the past 4 weeks" : float(avg_humidity)

        }

        Weather_analysis_collection.update_one(
        {
            "location" : "SOAC Sandpoint",
            "macAddress" : "54:32:04:41:6A:EC",
            "date" : week_date
        },
        {"$set" : weather_trends_record},
        upsert = True
        )





if __name__ == "__main__": 
    main()







        


    
