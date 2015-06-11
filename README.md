# NgsiConverter

The NgsiConverter is a python software that allows to transform csv files into an entry at a ContextBroker.

# Installing the software

Run setup.py in order to install all python required packages
```
   python setup.py install
```

# Config files

The first step is to define the config file, the config files have some fixed parameters and another that depends on the csv that you want to transform.

Every config file must have this thre sections parser_config, cb_config and csv_config.

1. At cb_config section it is defined the contextBroker configuration parameters like url, service_path, tenant and if a token is need or not.

2. At parser_config section you must describe the way that your csv is written, delimiter, quotechar, and pos_delimiter.

3. Finally csv_config section which have this fixed paramenters:

**entity_id**: the name of the column in your csv that is going to be used as id. If this parameter is set as empty and additional numeric column is added to the csv.

**id_prefix**: A prefix which is going to be concatenated with every entity_id, Tipically this parameter is used when entity_id has been set as empty.

**entity_type**: type of your entities (mandatory parameter)

**position_**: Here you can describe how the position is described at the csv file, this parameter aims to adapt the position to the recomended position format at a contextBroker.
For instance, if the position is defined in two of the columns of the csv named as Latitude and Longitude this parameter should be defined like position_: Latitude, Longitude. However if the position is defined in just one column the parameter should look like position_: name_of_the_column.

The variable parameters depends on the csv columns. For each column the config file must have the name which is going to have this attribute at the contextBroker and its type.
for example if the csv have the columns temperature and date:

temperature.name: temperature

temperature.type: float

date.name: timestamp

date.type: string

# Run the program

Run the program

python ngsi_converter.py -f [csv files] -cf [config files] -a [action]

-f: list of csv files

-cf:

one config file for each csv

one config file for all csv files

no config file, the program try to look for a default config file with the same name.

-a:

default 'APPEND', use 'DELETE' to remove a previous updated csv
