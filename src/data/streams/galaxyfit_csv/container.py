from zipfile import ZipFile
import warnings
from pathlib import Path
import pandas as pd
from pandas.core import indexing
import yaml
import csv
from collections import OrderedDict
from io import BytesIO, StringIO



def readFile(file, dtype):
    dict = OrderedDict()
    # file is an in-memory buffer
    with file as csvfile:
        if dtype in ('GALAXYFIT_HEARTRATE'):
            reader = csv.reader(csvfile, delimiter='\n')

        i = 0
        for row in reader:
            if i == 0:
                timestamp = float(row[0])
            elif i == 1:
                hertz = float(row[0])
            else:
                if i == 2:
                    pass
                else:
                    timestamp = timestamp + 1.0 / hertz
        		if dtype in ('GALAXYFIT_HEARTRATE'):
                    dict[timestamp] = row[0]
            i += 1
    return dict

def extract_data(data, sensor):
    sensor_data_file = BytesIO(data).getvalue().decode('utf-8')
    sensor_data_file = StringIO(sensor_data_file)
    column = sensor.replace("GALAXYFIT_", "").lower()

    # read sensor data
    if sensor in ('GALAXYFIT_HEARTRATE'):
        ddict = readFile(sensor_data_file, sensor)
        df = pd.DataFrame.from_dict(ddict, orient='index', columns=[column])
        df[column] = df[column].astype(float)
        df.index.name = 'timestamp'

    else:
        raise ValueError(
            "sensor has an invalid name: {}".format(sensor))

    # format timestamps
    df.index *= 1000
    df.index = df.index.astype(int)
    return(df)

def pull_data(data_configuration, device, sensor, container, columns_to_download):
    print("data_configuration", data_configuration) # { 'FOLDER': 'data/external/galaxyfit_csv }
    print("device", device) # 'p01'
    print("sensor", sensor) # galaxyfit_heartrate
    print("container", contatiner) # heartrate
    print("columns_to_download", columns_to_download)

    warning = True
    sensor_csv = container + '.csv'
    participant_data = pd.DataFrame(columns=columns_to_download.values())
    participant_data.set_index('timestamp', inplace=True)

    available_files = list((Path(data_configuration["FOLDER"]) / Path(container)).rglob("*.csv"))

    print("available_file: ", available_files)

    if len(available_files) == 0:
        warnings.warn("There were no files in: {}. ".format((Path(data_configuration["FOLDER"]) / Path(sensor))))

	# participant_data = extract_data(fileName,sensor)

    print("participant_data: ", participant_data)

	# participant_data.sort_index(inplace=True, ascending=True)
	# participant_data.reset_index(inplace=True)
	# participant_data.drop_duplicates(subset='timestamp', keep='first',inplace=True)
	# participant_data["device_id"] = device
    return(participant_data)

# print(pull_data({'FOLDER': 'data/external/empatica'}, "e01", "EMPATICA_accelerometer", {'TIMESTAMP': 'timestamp', 'DEVICE_ID': 'device_id', 'DOUBLE_VALUES_0': 'x', 'DOUBLE_VALUES_1': 'y', 'DOUBLE_VALUES_2': 'z'}))
