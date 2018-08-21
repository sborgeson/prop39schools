# setwd() to "your/path/to/prop39schools/R" directory
data_url = "https://s3.amazonaws.com/BrianCoffey/PGE_csv_2.zip"
data_file_zip = "data/PGE_csv_2.zip"
# save csv format of prop39 data to the project's data directory
download.file(data_url, data_file_zip)
unzip(data_file_zip)

weather_data_url = "https://s3.amazonaws.com/BrianCoffey/prop39_weather_dump.csv"
weather_data_file = "data/prop39_weather_dump.csv"
download.file(weather_data_url, weather_data_file)


