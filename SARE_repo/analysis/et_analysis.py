from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt 
from datetime import datetime 
import os 
import sys 

def main (): 
    load_dotenv()
    mongo_uri = os.getenv("MONGODB_URI")
     
    if "MONGODB_URI" not in os.environ:
        raise ValueError( "MongoDB_URI Enviroment Variable Is Missing")
    
    try: 
        client = MongoClient(mongo_uri)
        database = client["SCARECRO"]
        collection = database["ET_data"]
        et_summary_collection = database["ET_summary"]
        et_trends_collection = database["ET_trends"]
        df = pd.DataFrame(list(collection.find()))
    

    except Exception as e:
        print(f"Connection Failed:{e}")    
        sys.exit(1)

    # Use df[df to filter rows where location equals SOAC SANDPOINT
    # use .copy() to create a independent DataFrame so we modify the original
    sandpoint_df = df[df["location"]=="SOAC Sandpoint"].copy()

    # Convert time column from plain text string with "" to datetime objects
    # so pandas can perform date based calculations like sorting and resampling
    sandpoint_df["time"] = pd.to_datetime(sandpoint_df["time"])

    # Within the SOAC SANDPOINT locations sort rows chronologically by the time so data is in date order for analysis
    sandpoint_df = sandpoint_df.sort_values(by="time")

    # Create a new column called "et_7day_average" and then focus on column "et" and find it's last 7 record using .rolling (7) and find it's mean using .mean()
    sandpoint_df["et_7day_average"] = sandpoint_df["et"].rolling(7).mean()

    # Use .set_index to("time") to set the column time to index from data frame table so that it is easier for calculations
    sandpoint_df = sandpoint_df.set_index("time")


    # use .mean() to calulcate the average ET recorded
    average_et = sandpoint_df["et"].mean()
    print(f"Average ET for SOAC Sandpoint : {average_et}mm")

    # Use .max() to calculate highest ET
    highest_et = sandpoint_df["et"].max()
    print(f"Highest ET for SOAC Sandpoint : {highest_et}mm")

    # Use .idxmax() to find and identify the highest ET occured ever
    highest_et_index = sandpoint_df["et"].idxmax()
    print(f"Highest ET for SOAC Sandpoint occured on : {highest_et_index}") 
                          
    # Use .min() to find the lowest ET recorded
    lowest_et = sandpoint_df ["et"].min()
    print(f"Lowest ET for SOAC Sandpoint : {lowest_et}mm")

    # Use .sum() to calculate the combined ET data of all
    cummilative_et = sandpoint_df ["et"].sum()
    print(f"Cummulative ET for SOAC Sandpoint : {cummilative_et}mm")

    # Use resample("W") to filter column WEEK and use .mean() to find the weekly average
    weekly_average_et = sandpoint_df["et"].resample("W").mean()
    #print(f"Weekly Average ET for SOAC Sandpoint : {weekly_average_et}mm")

    # Use .idxmax() on "Weekly Average ET" to find the highest weekly average ET 
    highest_weekly_average_et = weekly_average_et.idxmax()
    print(f"Highest Weekly Average ET for SOAC Sandpoint occured on : {highest_weekly_average_et}")

    # Find the ET reocrd that is above the average calulated ET by focusing on the column "et" in sandpoint_df variable
    # and make it > average_et variable so it can give you any ET recorded that is above the average et
    et_above_average_caluclated_et = sandpoint_df[sandpoint_df["et"] > average_et]
    print(f"Number of Days With ET Above Average for SOAC Sandpoint : {len(et_above_average_caluclated_et)}")

    # Access the datetime index, convert to Series so .diff() can work on it
    # .diff() calculates the gap between each consecutive above-average ET date
    # Result: 1 day = consecutive, more than 1 day = streak broke
    date_gaps = et_above_average_caluclated_et.index.to_series().diff()

    # True = new streak started, False = streak continues
    is_new_streak = date_gaps != pd.Timedelta('1 days')
    # Assign a group number to each streak
    streak_groups = is_new_streak.cumsum()

    # Use .value_counts() to count how many days belong to each streak groups
    streak_lengths = streak_groups.value_counts()


    # Use .max() to find the highest number of consecutive days ET was above average
    longest_streak = streak_lengths.max()
    print(f"Longest Day Streak Of Above Average ET : {longest_streak}")

    # Use idx.max() to find which group number had the most consecutive days
    longest_streak_group = streak_lengths.idxmax()
    # Filter streak_groups to only show dates that belong to the longest streak group
    date_time_of_longest_streak = streak_groups[streak_groups == longest_streak_group]

    # Use .index.min() to find the lowest date when the longest streak occured
    streak_start = date_time_of_longest_streak.index.min()
    # Use .index.max() to find the highest date when the longest streak occured 
    streak_end = date_time_of_longest_streak.index.max()
    print(f"Longest Above Average ET Streak : {streak_start.strftime('%Y-%m-%d')} to {streak_end.strftime('%Y-%m-%d')}")

    weekly_average_et_present = weekly_average_et.iloc[-1]
    weekly_average_et_last_week = weekly_average_et.iloc[-2]
    last_two_weeks_percentile_comparison_calculation = ((weekly_average_et_present - weekly_average_et_last_week) / weekly_average_et_last_week) * 100

    if last_two_weeks_percentile_comparison_calculation < 0 : 
        print(f"ET Went Down {round(last_two_weeks_percentile_comparison_calculation, 2)}% Compared To Last Week")
    else : 
        print(f"ET Went up {round(last_two_weeks_percentile_comparison_calculation, 2)}% Compared To Last Week")

    et_summary_record = { 
        "location" : "SOAC Sandpoint",
        "average_et" : float(average_et),
        "highest_et" : float(highest_et),
        "highest_et_index" : (highest_et_index), 
        "lowest_et" : float(lowest_et),
        "cumulative_et" : float(cummilative_et),
        "longest_streak" : int(longest_streak),
        "streak_start" : streak_start,
        "streak_end" : streak_end,
        "last_two_weeks_percentile_comparison_calculation" : float(last_two_weeks_percentile_comparison_calculation),
        "last_updated_date_time" : datetime.now(),
        "days_above_average_et" : int(len(et_above_average_caluclated_et)),
        }
    
    et_summary_collection.update_one(
        {
            "location" : "SOAC Sandpoint"
        },
        {"$set" : et_summary_record},
        upsert = True
    )

    for week_date, week_et in weekly_average_et.items(): 
        #print(f"Fetching Data For : {week_date, week_et}")
    
    
        et_trends_record = { 
            "location" : "SOAC Sandpoint",
            "date" : week_date,
            "et_data" : week_et
            
         }

        et_trends_collection.update_one(
            {
                "location" : "SOAC Sandpoint",
                "date" : week_date
            },
            {"$set" : et_trends_record},
            upsert=True
    )
    




if __name__ == "__main__": 
    main()

    
