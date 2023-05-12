import pandapower as pp
import pandapower.plotting as plt

class PandaPowerWriter:
    def __init__(self, dictEquipmentIDtoType, dictEquipment) -> None:
        self.equipmentIDtoType = dictEquipmentIDtoType
        self.equipment = dictEquipment
        self.network = None
        self.busDict = {}

    def initialiseNetwork(self):
        """
        Creates empty pandapower network
        """
        net = pp.create_empty_network() 
        self.network = net
        # Implement equipment in pandapower
        self.initialiseBuses()
        self.initialiseLines()
        self.initialiseSwitches()
        self.initialiseLoads()
        self.initialiseTransformer()
        self.initialiseStaticGen()
        self.initialiseMachines()
        self.initialiseShunt()
        self.initialiseWard()
    
    def getVoltageLevel(self, nodeID):
        """
        Returns a float of the voltage level associated with a node
        """
        voltageLevelID = self.equipment["ConnectivityNode"][nodeID]['ConnectivityNode.ConnectivityNodeContainer']
        return float(self.equipment["VoltageLevel"][voltageLevelID.replace("#", "")]['IdentifiedObject.name'])

    def toHTML(self, htmlFileName = "network.html"):
        """
        Outputs a HTML file in the htmlOutput folder of the current network
        """
        plt.to_html(self.network, "htmlOutput/"+htmlFileName)
        return None

    def getAssociatedSubstation(self, nodeID) :
        """ 
        Returns a string with the Name of a Substation related to some equipment
        """
        voltageLevelID = self.equipment[self.equipmentIDtoType[nodeID]][nodeID]['ConnectivityNode.ConnectivityNodeContainer']
        substationID = self.equipment[self.equipmentIDtoType[voltageLevelID]][voltageLevelID]['VoltageLevel.Substation']
        substationName = self.equipment[self.equipmentIDtoType[substationID]][substationID]['IdentifiedObject.name']
        return substationName
    
    def getAssociatedBus(self, terminalID):
        """
        Returns a string with the ID of a Connectivity Node that corresponds with a particular terminalID
        """
        nodeID = self.equipment["Terminal"][terminalID]['Terminal.ConnectivityNode']
        return nodeID

            
    def getLineMaxCurrent(self, lineID):
        """
        Returns the Current Limit of a Line as a float
        """
        answer = None
        for key, value in self.equipment["CurrentLimit"].items():
            currentLimit = value["CurrentLimit.value"]
            OperationalLimitID = value["OperationalLimit.OperationalLimitSet"]
            terimnalID = self.equipment[self.equipmentIDtoType[OperationalLimitID]][OperationalLimitID]["OperationalLimitSet.Terminal"]
            checkAgaisnt = self.equipment[self.equipmentIDtoType[terimnalID]][terimnalID]["Terminal.ConductingEquipment"]
            if checkAgaisnt == lineID:
                answer = currentLimit
            
        return float(answer)/1000

    def initialiseBuses(self, newBusID = None):
        """ 
        Creates the buses
        Defaults newBusID as None
        In case you pass it a variable, it creates a new bus because of T1 _BE_V2-2 and T1_NL_V2
        """
        if newBusID == None:
            counter = 0
            for terminal, terminalInfo in self.equipment["ConnectivityNode"].items():
                
                print(terminalInfo)
                node = pp.create_bus(self.network, name='Node %s' % counter, vn_kv=self.getVoltageLevel(terminal), type='n',
                            origin_id = terminal, zone = self.getAssociatedSubstation(terminal))
                counter += 1
                self.busDict[terminal] = node
        else:
            node = pp.create_bus(self.network, name='Node %s' % len(self.busDict), type='n', vn_kv='nan',
                    origin_id = newBusID)  
            self.busDict[newBusID] = node 

    def initialiseLines(self):
        """ 
        Creates the lines in the PandaPower network
        """

        for lineID, lineInfo in self.equipment["ACLineSegment"].items():
            terminalID0, terminalID1 = lineInfo['associatedTerminals']

            #if there is a KeyError here, it means that the connectivity node does not exist yet. 
            #we create a new connectivity node then
            try:
                fromBus = self.busDict[self.getAssociatedBus(terminalID0)]
            except:
                self.initialiseBuses(self.getAssociatedBus(terminalID0))
                fromBus = self.busDict[self.getAssociatedBus(terminalID0)]
            try:
                toBus = self.busDict[self.getAssociatedBus(terminalID1)]
            except:
                self.initialiseBuses(self.getAssociatedBus(terminalID1))
                toBus = self.busDict[self.getAssociatedBus(terminalID1)]


            #create line
            pp.create_line_from_parameters(self.network, fromBus, toBus, 
                                           length_km = float(lineInfo['Conductor.length']), 
                                           r_ohm_per_km = float(lineInfo['ACLineSegment.r'])/float(lineInfo['Conductor.length']), 
                                           x_ohm_per_km = float(lineInfo['ACLineSegment.x'])/float(lineInfo['Conductor.length']), 
                                           c_nf_per_km = 1e9*float(lineInfo['ACLineSegment.bch'])/float(lineInfo['Conductor.length']), 
                                           name= lineInfo['IdentifiedObject.name'], 
                                           index=None, type=None, geodata=None, 
                                           in_service=True, 
                                           df=1.0, parallel=1, 
                                           max_i_ka = self.getLineMaxCurrent(lineID),
                                           g_us_per_km=  1e6*float(lineInfo['ACLineSegment.gch'])/float(lineInfo['Conductor.length']), 
                                           r0_ohm_per_km=float(lineInfo['ACLineSegment.r0'])/float(lineInfo['Conductor.length']), 
                                           x0_ohm_per_km=float(lineInfo['ACLineSegment.x0'])/float(lineInfo['Conductor.length']), 
                                           c0_nf_per_km= 1e9*float(lineInfo['ACLineSegment.b0ch'])/float(lineInfo['Conductor.length']), 
                                           g0_us_per_km= 1e6*float(lineInfo['ACLineSegment.g0ch'])/float(lineInfo['Conductor.length']), 
                                           origin_id = lineID)

    def initialiseSwitches(self):
        """ 
        Creates the switches in PandaPower network
        """
        for switchID, switchInfo in self.equipment["Breaker"].items():
            terminalID0, terminalID1 = switchInfo['associatedTerminals']
            fromBus = self.busDict[self.getAssociatedBus(terminalID0)]
            toBus = self.busDict[self.getAssociatedBus(terminalID1)]
            

            #watch for the strange double negative here: normalOpen == true means that isClosed = False
            isClosed = True
            if switchInfo['Switch.normalOpen'] == 'true':
                isClosed = False
            pp.create_switch(self.network, fromBus, toBus, et="b", type="CB", closed=isClosed)


    def initialiseTransformer(self):
        """
        Creates transformer objects in the PandaPower network
        """
        for transformerID, transformerInfo in self.equipment["PowerTransformer"].items():
            if len(transformerInfo['associatedTerminals']) == 2:
                terminalID0, terminalID1 = transformerInfo['associatedTerminals']
                hvBus = self.busDict[self.getAssociatedBus(terminalID0)]
                lvBus = self.busDict[self.getAssociatedBus(terminalID1)]
                pp.create_transformer(self.network, hvBus, lvBus, name=transformerInfo['IdentifiedObject.name'], 
                std_type="25 MVA 110/20 kV", origin_id = transformerID)
            
            elif len(transformerInfo['associatedTerminals']) == 3:
                terminalID0, terminalID1, terminalID2 = transformerInfo['associatedTerminals']
                hvBus = self.busDict[self.getAssociatedBus(terminalID0)]
                mvBus = self.busDict[self.getAssociatedBus(terminalID1)]
                lvBus = self.busDict[self.getAssociatedBus(terminalID2)]
                pp.create_transformer3w(self.network, hvBus, mvBus, lvBus, std_type = '63/25/38 MVA 110/20/10 kV',
                 name=transformerInfo['IdentifiedObject.name'], origin_id = transformerID)


    
    def initialiseLoads(self):
        """
        Creates load objects in the Pandapower network
        """
        for loadID, loadInfo in self.equipment["EnergyConsumer"].items():
            terminalID = loadInfo['associatedTerminals'][0]
            atBus = self.busDict[self.getAssociatedBus(terminalID)]
            pp.create_load(self.network, atBus, p_mw= loadInfo['EnergyConsumer.p'], q_mvar=loadInfo['EnergyConsumer.q'], scaling=1.0, name= loadInfo['IdentifiedObject.name'], origin_id = loadID)


    def initialiseStaticGen(self):
        """
        Creates a static generator object in the Pandapower network
        """
        for generatorID, generatorInfo in self.equipment["EnergySource"].items():
            terminalID = generatorInfo['associatedTerminals'][0]
            atBus = self.busDict[self.getAssociatedBus(terminalID)]
            pp.create_sgen(self.network , atBus, p_mw= -float(generatorInfo['EnergySource.activePower']), 
                           q_mvar= -float(generatorInfo['EnergySource.reactivePower']), 
                           name= generatorInfo['IdentifiedObject.name'],
                           origin_id= generatorID, 
                           rx = float(generatorInfo['EnergySource.r']))/float(generatorInfo['EnergySource.x'])
            

    def initialiseMachines(self):
         """
         Creates generator objects in PandaPower
         """
         for generatorID, generatorInfo in self.equipment["SynchronousMachine"].items():
            terminalID = generatorInfo['associatedTerminals'][0]
            atBus = self.busDict[self.getAssociatedBus(terminalID)]
            pp.create_gen(self.network, atBus, p_mw= -float(generatorInfo['RotatingMachine.p']),
                           max_q_mvar= float(generatorInfo['SynchronousMachine.maxQ']), 
                           min_q_mvar= float(generatorInfo['SynchronousMachine.minQ']), 
                           vm_pu= float(self.getVoltageLevel(self.getAssociatedBus(terminalID)))/float(generatorInfo['RotatingMachine.ratedU']), 
                           sn_mva = float(generatorInfo['RotatingMachine.ratedS']),
                           name= generatorInfo['IdentifiedObject.name'],
                           origin_id = generatorID)      

    def initialiseShunt(self):
         """
         Creates linear shunts in PandaPower
         """
         for shuntID, shuntInfo in self.equipment["LinearShuntCompensator"].items():
            terminalID = shuntInfo['associatedTerminals'][0]
            atBus = self.busDict[self.getAssociatedBus(terminalID)]
            q = 0
            if float(shuntInfo['LinearShuntCompensator.bPerSection']) > 0:
                q = float(shuntInfo['LinearShuntCompensator.bPerSection'])*float(shuntInfo['ShuntCompensator.normalSections'])
                q = -float(shuntInfo['ShuntCompensator.nomU'])**2*q
            
            p = 0
            if float(shuntInfo['LinearShuntCompensator.gPerSection']) > 0:
                p = float(shuntInfo['LinearShuntCompensator.gPerSection'])*float(shuntInfo['ShuntCompensator.normalSections'])
                p = -float(shuntInfo['ShuntCompensator.nomU'])**2*p
            pp.create_shunt(self.network, atBus, 
                            q_mvar= q, 
                            p_mw= p, 
                            name=shuntInfo['IdentifiedObject.name'], 
                            origin_id= shuntID)       

    def initialiseWard(self):
         """
         Creates ward objects in PandaPower
         """
         for wardID, wardInfo in self.equipment["EquivalentInjection"].items():
            terminalID = wardInfo['associatedTerminals'][0]
            atBus = self.busDict[self.getAssociatedBus(terminalID)]
            pp.create_ward(self.network, atBus, 
                           ps_mw = float(wardInfo['EquivalentInjection.p']), 
                           qs_mvar = float(wardInfo['EquivalentInjection.q']), 
                           pz_mw = float(wardInfo['EquivalentInjection.r']), 
                           qz_mvar = float(wardInfo['EquivalentInjection.r']), 
                           name= wardInfo['IdentifiedObject.name'],
                           origin_id = wardID)        
