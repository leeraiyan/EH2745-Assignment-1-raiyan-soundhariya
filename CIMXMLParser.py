import re
import xml.etree.ElementTree as ET

ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'}

class Graph:
    def __init__(self):
        self.vertices = {}

    def add_vertex(self, vertex):
        self.vertices[vertex] = []

    def add_edge(self, source, destination):
        self.vertices[source].append(destination)
        self.vertices[destination].append(source)

    def get_adjacent_vertices(self, vertex):
        return self.vertices[vertex]


class CIM_XML_parser:
    def __init__(self, eqPath, sshPath = None) -> None:
        """
        A class that handles all parsing and reading of EQ and SSH files
        Stores all data as dictionaries
        """

        eqTree = ET.parse(eqPath)
        self.eqRoot = eqTree.getroot()
        sshTree = ET.parse(sshPath)
        self.sshRoot = sshTree.getroot()

        #graph of the network
        self.networkGraph = Graph()

        self.equipmentIDtoType = {}

        self.equipment = {
            "Substation": {},
            "BaseVoltage":{},
            "VoltageLevel":{},
            "GeneratingUnit":{},
            "SynchronousMachine":{},
            "RegulatingControl":{},
            "PowerTransformer":{},
            "EnergyConsumer":{},
            "PowerTransformerEnd":{},
            "Breaker":{},
            "RatioTapChanger":{},
            "Region":{},
            "EquipmentContainer":{},
            "ACLineSegment":{},
            "BusbarSection":{},
            "ConnectivityNode":{},
            "Terminal":{},
            "Line":{},
            "ConnectivityNodeContainer":{},
            "LinearShuntCompensator":{},
            "RatioTapChanger":{},
            "PhaseTapChangerAsymetrical":{},
            "EnergySource":{},
            "EquivalentInjection":{},
            "PetersenCoil":{},
            "CurrentLimit": {},
            "OperationalLimitSet": {}
        }

    def search_key(self, key):
        """
        Returns a string with information regarding a particular ID in the equipment dictionary
        """
        if key in self.equipment:
            return self.equipment[key]
        else:
            for value in self.equipment.values():
                if isinstance(value, dict):
                    result = self.search_key(value, key)
                    if result is not None:
                        return result
        print("Nothing Related")

    def getEquipmentDict(self, equipmentID):
        """
        Returns a dictionary object whose key is the ID passed to this function
        param equipmentID: string that identifies a piece of electrical equipment
        """
        key = self.getEquipmentType(equipmentID)
        return self.equipment[key][equipmentID]
    
    def getEquipmentType(self, equipmentID):
        """
        Returns a string that specifies the type of electrical equipment
        param equipmentID: string that identifies a piece of electrical equipment
        """
        try:
            return self.equipmentIDtoType[equipmentID]
        except:
            return None
        
    def associateTerminaltoEquipment(self):
        """
        Associates all electrical equipment with the corresponding terminal IDs
        """
        counter = 0
        for terminal, terminalInfo in self.equipment["Terminal"].items():
            counter += 1
            equipmentID = terminalInfo["Terminal.ConductingEquipment"].replace("#", "")
            equipmentType = self.getEquipmentType(equipmentID)
            self.equipment[equipmentType][equipmentID]["associatedTerminals"].append(terminal)
            # print(counter, "/", len(self.equipment["Terminal"]), "Associated Terminal", terminal, "with Equipment", equipmentID, self.getEquipmentType(equipmentID))
        return None

    def investigate(self, equipmentID):
        """
        Helper function for developers to obtain details about connections between electrical equipment
        """
        dictionary = self.getEquipmentDict(equipmentID)

        print(self.getEquipmentType(equipmentID))
        for key, value in dictionary.items():
            if len(value) > 0:
                if value[0] == '_':
                    print(re.sub(r'^.*?\.', '', key), value , "<-" , self.getEquipmentType(value.replace("#", "")))

                else:
                    print(re.sub(r'^.*?\.', '', key), value)
        return None

    def runEQ(self):
        """
        Parses the EQ file and stores all information in a Dict = {Dict: {Dict: {string}}}} format in self.equipment attribute
        """
        for node in self.eqRoot:
            #check equipment type
            # logging.info(node.tag.replace("{"+ns['cim']+"}",""))
            equipmentType = node.tag.replace("{"+ns['cim']+"}","")

            #obtain ID of equipment first
            newKey = node.attrib.get(ns['rdf']+'ID')

            
            # logging.info("ID:", node.attrib.get(ns['rdf']+'ID'))

            #empty dictionary for information of the equipment above
            newValue = {}
            #populate empty dictionary with information if it is an important equipment
            if equipmentType in self.equipment.keys():
                for leaf in node:

                    #this is an rdf resource
                    if leaf.text == None:
                        newValue[leaf.tag.replace("{"+ns['cim']+"}","")] = leaf.attrib.get(ns['rdf']+'resource').replace("#", "")
                        # logging.info(leaf.tag.replace("{"+ns['cim']+"}",""), leaf.attrib.get(ns['rdf']+'resource'))
                    
                    #this is just normal text information
                    else:
                        # print(re.sub(r"\b{http\S*", "", leaf.tag), leaf.text
                        newValue[leaf.tag.replace("{"+ns['cim']+"}","").replace("{"+ns['entsoe']+"}","")] = leaf.text
                        # logging.info(leaf.tag.replace("{"+ns['cim']+"}","").replace("{"+ns['entsoe']+"}",""), leaf.text)


                self.equipmentIDtoType[newKey] = equipmentType
                newValue["associatedTerminals"] = []
                self.equipment[equipmentType][newKey] = newValue

    def runSSH(self):
        """
        Updates existing data in self.equipment attribute
        """
        for node in self.sshRoot:

            #check equipment type
            equipmentType = node.tag.replace("{"+ns['cim']+"}","")

            #check ID of equipment
            equipmentID = node.attrib.get(ns['rdf']+'about').replace("#", "")

            if equipmentType in self.equipment.keys():
                equipmentDict = self.equipment[equipmentType][equipmentID]
                for leaf in node:
                    #this is an rdf resource
                    if leaf.text == None:
                        attribute = leaf.tag.replace("{"+ns['cim']+"}","")
                        value =leaf.attrib.get(ns['rdf']+'resource').replace("#", "")
                        try:
                            if equipmentDict[attribute] != value:
                                oldValue = equipmentDict[attribute]
                                equipmentDict[attribute] = value
                                # print(attribute, "changed from", oldValue, "to", equipmentDict[attribute])
                        except:
                            equipmentDict[attribute] = value
                            # print(attribute, "added:",  equipmentDict[attribute])
                    #this is just normal text information
                    else:
                        attribute = leaf.tag.replace("{"+ns['cim']+"}","").replace("{"+ns['entsoe']+"}","")
                        value = leaf.text
                        try:
                            if equipmentDict[attribute] != value:
                                oldValue = equipmentDict[attribute]
                                equipmentDict[attribute] = value
                                # print(attribute, "changed from", oldValue, "to", equipmentDict[attribute])
                        except:
                            equipmentDict[attribute] = value
                            # print(attribute, "added:",  equipmentDict[attribute])

            else:
                pass
                # print("Not interested in", equipmentType)


    def run(self):
        """
        Overall function that calls private methods within the class
        """
        self.runEQ()
        self.associateTerminaltoEquipment()
        self.runSSH()

        return self.equipmentIDtoType, self.equipment