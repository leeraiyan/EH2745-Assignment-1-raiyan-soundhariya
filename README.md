# EH2745 Assignment 1

A desktop application that converts EQ and SSH XML files from the Common Information Model to a PandaPower network. The results can be viewed using the built-in GUI. 

## Features
* Fully-functional and intuitive GUI
* Browsable imports of EQ and SSH XML files
* Is able to handle MOST cases of EQ and SSH XML Files
* Handles connections between certain missing Connectivity Nodes
* Plots the results in a graph
* Provides information about equipment in the network
* Catches errors gracefully

## Installation Instructions
1. Clone this repository
2. Use Python 3.9 to run `pip install -r requirements.txt`
3. Use Python 3.9 to run `python gui.py` (NOTE: Testing shows that Python 3.10 is not supported due to dependencies)


![Main UI](docs/images/ui.png)

![Results Page](docs/images/results.png)

## Python Files Included
Project is created with:
* `CIMXMLParser.py`: Contains the class `CIM_XML_parser`
* `PandaPowerManager.py`: Contains the class `PandaPowerWriter`
* `gui.py`: Contains GUI-related information

## Class Information
* `CIM_XML_parser` class handles all reading of the EQ and SSH files. It stores the data of the files into a dictionary of all the equipment in the grid. This dictionary is kept as an attribute of the class. This class also contains several important methods:
  - ' __init__(self, eqPath, sshPath=None)': The constructor method for the CIM_XML_parser class. It initializes the object and sets up the necessary attributes, including parsing the EQ and SSH XML files.
  - 'search_key(self, key)': Searches for a given key in the equipment dictionary and returns a string with information related to that key.
  - 'getEquipmentDict(self, equipmentID)': Retrieves a dictionary object from the equipment dictionary based on the provided equipment ID.
  - 'getEquipmentType(self, equipmentID)': Returns the type of electrical equipment corresponding to the given equipment ID.
  - 'associateTerminaltoEquipment(self)': Associates all electrical equipment with their corresponding terminal IDs.
  - 'investigate(self, equipmentID)': Prints details about connections between electrical equipment, based on the provided equipment ID.
  - 'runEQ(self)': Parses the EQ file and stores all the information in a nested dictionary format in the equipment attribute.
  - 'runSSH(self)': Updates existing data in the equipment attribute using the information from the SSH file.
  - 'run(self)': A high-level method that executes the necessary steps to parse and process the XML files, returning the equipmentIDtoType and equipment dictionaries.

* `PandaPowerWriter` class is initialised by passing the outputs of the `CIM_XML_parser.run()` function. It handles the conversion of all equipment information into the creation format of a PandaPower network instance and its various equipment. It contains the following methods:




