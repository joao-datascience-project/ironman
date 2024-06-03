# Global Variables

INDOOR_VAR = ['Virtual Cycling','Indoor Cycling']



######### Auxiliary Functions ############

def rouvy_check(value):
	"""
	Checks for rouvy 
	"""
    lower_value = value.lower()

    if 'rouvy' in lower_value:
        return 'Rouvy'
    else:
        return 'Indoor Bike'

def clean_comma_num(data,i):
	"""
	REMOVES ',' NUM VAR
	"""
	#data[i] = data[i].apply(lambda x: int(x.replace(',','')))
	data[i] = data[i].apply(lambda x: int(x.replace(',', '')) if isinstance(x, str) else x)
	return data

def clean_dash(data):
	"""
	TRANSFORM '--' to NaN if exists
	"""
	for i in data.columns:
		if '--' in  data[i].unique():
			data[i] = np.where(data[i]=='--', np.nan, data[i])

	return data

def clean_0_in_numeric(data):
	"""
	TRANSFORM 0 to NaN if exists in numeric columns
	"""
	for i in data.select_dtypes(include='number').columns:
		data[i] = np.where(data[i]==0, np.nan, data[i])

	return data

def clean_hr_under60(data):
	"""
	TRANSFORM TO NAN WHEN HR COLUMNS ARE LESS THAN 60
	"""

	for i in [i for i in data.columns if '_hr' in i]:
		mask = (data[i]< 60)

		data[i] = np.where(mask,np.nan,data[i])

	return data

def clean_temp_zero_diff(data):
	"""
	Transform to NaN if diff between max and min temp = 0
	"""

	mask = (data['max_temp'] - data['min_temp']) == 0

	data = data.assign(max_temp=np.where(mask, np.nan, data['max_temp']),
                       min_temp=np.where(mask, np.nan, data['min_temp']))

	return data

def remove_second_comma(s):
    parts = s.split(',')
    if len(parts) > 2:
        parts.pop(1)  # Remove the second comma if it exists
    return ','.join(parts)

def clean_avg_str_length0(data):
    """
    TRANSFORM TO NAN WHEN AVG_STR_LENGTH VALUE ARE 0
    """
    for col in ['avg_stride_length']:
        if col in data.columns:
            mask = (data[col]==0)

            data[col] = np.where(mask,np.nan, data[col])
    
    return data

########### Main Functions ################
def load_data(path):
	"""
	READ CSV AND PERFORM BASIC ENGINEERING STEPS
	ID
	LOWERCASE AND _
	ONLY AFTER JULY 23
	SEPARATE DATE AND TIME OF THE DAY
	"""

		# Read CSV

	df = pd.read_csv(path,parse_dates=['Date'])


		# Create Unique ID based on Nanoseconds

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

	return df


#### SWIM pre-processing function ######

def swim_eng_func(path):
	"""
	SWIM ENGINEERING FUNCTION

	TRANSFORMS THE SWIM DATA:
		REMOVES UNNECESSARY COLUMNS
		REMOVE ',' IN DISTANCE AND TYPECAST IT TO INT
		REPLACE ALL NON NUMERIC CARACT TO NAN
		REPLACE 0 IN NUM COLS TO NAN
	"""

	swim_data = load_data(path)

		# Dropping Unique columns plus 'title','moving_time','best_lap_time'

	cols_to_drop = []
	for i in swim_data.columns:
		if swim_data[i].nunique() == 1:
			cols_to_drop.append(i)
	for j in ['title', 'moving_time','best_lap_time']:
			if j in swim_data.columns:
				cols_to_drop.append(j)

	swim_data2 = swim_data.drop(columns=cols_to_drop)

		# Remove the ',' in distance and transform it to int

	swim_data2['distance'] = swim_data2['distance'].apply(lambda x: int(x.replace(',','')))

		# Replace all '--' by nan

	for i in swim_data2.columns:
		if '--' in  swim_data2[i].unique():
			swim_data2[i] = np.where(swim_data2[i]=='--', np.nan, swim_data2[i])


		# replace all 0 in numeric features by nan
	for i in swim_data2.select_dtypes(include='number').columns:
		swim_data2[i] = np.where(swim_data2[i]==0, np.nan, swim_data2[i])

		# Remove dots from column names
	swim_data2.columns = [col.replace('.', '') for col in swim_data2.columns]


	return swim_data2

def open_swim(data):

		# Obtain the string that encodes open water
	open_string = [i for i in list(data['activity_type'].unique()) if 'Open' in i][0]

		# filter open water data
	open_data = data.loc[data['activity_type']== open_string]

	cols_to_drop=[]
	for i in  ['avg_swolf',
	           'number_of_laps',
	           'elapsed_time',
	           'max_hr']:
	    if i in open_data.columns:
	    	cols_to_drop.append(i)
	open_data.drop(columns=cols_to_drop, inplace=True)

	return open



## Bike Pre-Processing Function 


def bike_eng_function(path):
	"""
	BIKE ENGINEERING FUNCTION

	TRANSFORMS THE BIKE DATA:
		REMOVES UNNECESSARY COLUMNS
		REMOVE ',' IN DISTANCE AND TYPECAST IT TO INT
		REPLACE ALL NON NUMERIC CARACT TO NAN
		REPLACE 0 IN NUM COLS TO NAN
	"""


	bike_data = load_data(path)

		# Remove unnecessary columns

	cols_to_drop = []
	for i in bike_data.columns:
		if bike_data[i].nunique() == 1:
			cols_to_drop.append(i)
	for j in ['title', 
	      'moving_time',
		  'best_lap_time',
		  'index',
		  'avg_stroke_rate',
		  'number_of_laps',
		  'elapsed_time']:
		if j in bike_data.columns:
			cols_to_drop.append(j)
	bike_data = bike_data.drop(columns =cols_to_drop)

		# REMOVES ',' NUM COL

	for i in ['min_elevation', 'max_elevation']:
		bike_data = clean_comma_num(bike_data,i)	

		# NaN when diff temp is 0
	if 'max_temp' and 'min_temp' in bike_data.columns:
		bike_data = clean_temp_zero_diff(bike_data)

		# NaN when _hr features less than 60
	bike_data = clean_hr_under60(bike_data)

		# '--' to Nan
	bike_data = clean_dash(bike_data)

		# 0 in numeric columns to Nan
	bike_data = clean_0_in_numeric(bike_data)

		# Deal with wrong format in distance
	if 'distance' in bike_data.columns:
		bike_data['distance'] = bike_data['distance'].str.replace('.',',')\
		                                             .apply(remove_second_comma)\
		                                             .str.replace(',','.')

	return bike_data

def road_bike(data):
	"""
	SELECTS ROAD BIKE DATA AND CLEAN IT
	"""

	#data = bike_eng_function(path)

		# Select Road Bike Data
	road_data = data.loc[data['activity_type']=='Cycling']

		# Get location and drop title

	road_data['Location'] = road_data['title'].apply(lambda x: x.replace(' Cycling',''))

		# Drop Unique columns and 100% Nan

	cols_to_drop = []
	for i in road_data.columns:
		if road_data[i].nunique() == 1:
			cols_to_drop.append(i)
	road_data = road_data.drop(columns=cols_to_drop +['title'])	
	
	# drop all columns with 100% NaN

	road_data.dropna(axis=1, how='all',inplace=True)

	return road_data

def indoor_bike(data):
	"""
	SELECTS INDOOR BIKE DATA AND CLEAN IT
	ibd - indoor bike data
	"""

	#data = bike_eng_function()

	ibd = data.loc[data['activity_type'].isin(INDOOR_VAR)]

	for i in ['min_elevation', 'max_elevation']:
		ibd = clean_comma_num(ibd,i)

	ibd['indoor_type'] = ibd['title'].apply(rouvy_check)

	ibd = ibd.drop(columns=['aerobic_te',
							'min_temp',
							'max_temp',
							'title'])

	return ibd

def run_eng_function(path):

	run_data = load_data(path)

	# Remove unnecessary columns
	run_cols_to_drop = []
	for col in ['best_lap_time',
	            'favorite',
	            'avg_stroke_rate',
	            'total_reps',
	            'surface_interval',
	            'decompression',
	            'flow',
	            'dive_time',
	            'avg._swolf',
	            'avg_vertical_ratio',
	            'avg_vertical_oscillation',
	            'avg_ground_contact_time',
	            'training_stress_score®',
	            'avg_power',
	            'max_power',
	            'grit',
	            'flow']:
	    if col in run_data.columns:
	        run_cols_to_drop.append(col)

	run_data = run_data.drop(columns=run_cols_to_drop)

	# NaN when diff temp is 0
	if 'max_temp' and 'min_temp' in run_data.columns:
	    run_data = clean_temp_zero_diff(run_data)   

	# NaN when _hr features less than 60
	run_data = clean_hr_under60(run_data)

	# '--' to Nan
	run_data = clean_dash(run_data)

	# Nan when 0 in avg_stride_length
	run_data = clean_avg_str_length0(run_data)

	# Get Location and Drop Title
	run_data['location'] = run_data['title'].apply(lambda x: x.split('Running')[0])

	run_data = run_data.drop(columns=['title'])

	










