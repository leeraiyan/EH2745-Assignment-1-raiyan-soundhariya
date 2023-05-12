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
2. Use Python 3.9 to run `pip install -r requirements.txt` (NOTE: It is known from testing that Python 3.10 is not supported due to dependencies)
3. Use Python 3.9 to run `python gui.py`(NOTE: It is known from testing that Python 3.10 is not supported due to dependencies)


![Main UI](docs/images/ui.png)

![Results Page](docs/images/results.png)

## Python Files Included
Project is created with:
* `CIMXMLParser.py`: Contains the class `CIM_XML_parser`
* `PandaPowerManager.py`: Contains the class `PandaPowerWriter`
* `gui.py`: Contains GUI-related information

## Class Information
* `CIM_XML_parser` class handles all reading of the EQ and SSH files. It stores the data of the files into a dictionary of all the equipment in the grid. This dictionary is kept as an attribute of the class. This class also contains several important functions:
*   test
* `PandaPowerWriter` class is initialised by passing the outputs of the `CIM_XML_parser.run()` function. It handles the conversion of all equipment information into the creation format of a PandaPower network instance and its various equipment. It contains the following functions:




