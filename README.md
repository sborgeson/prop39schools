# prop39schools
CA proposition 39 funded energy efficiency efforts in K-12 schools with the requirement that their utility (electricity and natural gas) consumption and project details be publicly disclosed. The result is a public data set that allows exploration of patterns of energy consumption in schools and examination of the impacts of efficiency interventions on energy consumption. More information and the data itself can be found here:

http://www.energy.ca.gov/efficiency/proposition39/data/

To work with this data through this project:

1. Clone this project into a locaiton we will call your 'project directory'. `git clone git@github.com:sborgeson/prop39schools.git`.
2. Next download the 2.5 GB of meter and project data found here into your project directory http://www.energy.ca.gov/efficiency/proposition39/data/IOU_Data.zip
3. You can also download an Excel file of project and school metadata from http://www.energy.ca.gov/efficiency/proposition39/data/PEPS_Data.xlsx
4. Unzip the contents of the `IOU_Data.zip` into a sub-directory of your project directory called `IOU_Data`. IOU_Data should have sub-directories called LADWP, PGE, SCE, SDGE, and SCG. Not that the data will expand to over 100 GB in size!! Make sure you have room.
5. While thte full data set is downloading, you can extract `sample_data.zip` into a `sample_data` directory and get starting with running the data parser and conversion utility script p39toCSV.py.

p39toCSV.py can pull school metadata, monthly billing data and interval meter readings from the complex xml data structure for each school and convert them into billing and interval csv formats, which are much more compact and analysis friendly than their XML counterparts.

TODO: At the moment, p39toCSV is hard coded to conver files in a fixed directory, currently the sample_data directory. We need to support passing in the directory to use as a command line argument.
