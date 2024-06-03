import pandas as pd
import numpy as np
import settings as set


"""
AUX FUNCTIONS
"""



def read_garmin():
    """
    Function that read directly the garmin csv 
    """
    df = pd.read_csv(set.CSV_PATH,parse_dates=['Date'])

    # Unique ID Creation based on Nanoseconds

    df['ID'] = df['Date'].astype(int) // 10**9
    
    # Set the ID column as the first column of the dataset

    first_column = df.pop('ID') 

    df.insert(0, 'ID', first_column)

    # Lowercase all the columns

    df.columns = [col.replace(' ', '_').lower() for col in df.columns]

    # Select data only after september 2023

    df = df.loc[df.date>'2023-09-07']

    # Separate date and time_day columns

    df['time_day'] = df['date'].dt.time

    df['date'] = df['date'].dt.date

    # Drop Unnecessary Columns

    df = df.drop(columns=['moving_time',
                          'favorite',
                          'avg_vertical_ratio',
                          'avg_vertical_oscillation',
                          'avg_ground_contact_time',
                          'grit',
                          'flow',
                          'decompression',
                          'surface_interval',
                          'dive_time',
                          'total_reps'
                          ])

    return df

def custom_t_zone(value):
    """
    Maps the training zone by custom values
    """

    if  194 > value >= 178:
        return 5
    elif 178 > value >= 160:
        return 4
    elif 160 > value >= 141:
        return 3
    elif 141 > value >= 122:
        return 2
    elif 122 > value > 40:
        return 1
    else:
        return np.nan
    


def running_engineering(data):
    """
    Engineering step for creating the Running Data
    """


    data_running = data.query("activity_type=='Running'")

    # Drop Unnecessary running columns


    data_running = data_running.drop(columns=[column for column in data_running.columns if data_running[column].nunique() == 1]+['best_lap_time',
                                                                                                                                 'number_of_laps',
                                                                                                                                 'distance.1',
                                                                                                                                 'total_descent.1',
                                                                                                                                 'elapsed_time'])
    
        # Typecast to numeric the numeric features
    for var in set.RUN_VAR_TO_NUMERIC:
        data_running[var] = pd.to_numeric(data_running[var], errors='coerce')


        # Creates the Run Location 
    data_running['run_location'] = data_running.title.str.replace(r'\bRunning\b.*$', '', regex=True)

        # Transforms the time column as a timedelta
    data_running['time'] = pd.to_timedelta(data_running['time'])


        # Mask when diff between max_temp and min_temp is 0
    mask = (data_running['max_temp'] - data_running['min_temp']) == 0

    
    data_running = data_running.assign(avg_hr=np.where(data_running['avg_hr'] == 0, np.nan, data_running['avg_hr']),
                                   max_hr=np.where(data_running['max_hr'] == 0, np.nan, data_running['max_hr']),
                                   avg_stride_length = np.where(data_running['avg_stride_length'] == 0, np.nan, data_running['avg_stride_length']),
                                   max_temp=np.where(mask, np.nan, data_running['max_temp']),
                                   min_temp=np.where(mask, np.nan, data_running['min_temp']))
    

    return data_running