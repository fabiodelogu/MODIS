"""
Class Features

Name:          Drv_Data_DB
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20150806'
Version:       '1.0.1'
"""

######################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

# Libraries
import os
import datetime
import numpy as np

from Drv_Data_IO import Drv_Data_IO

from GetException import GetException
######################################################################################

#-------------------------------------------------------------------------------------
# Class GetMeteoData
class Drv_Data_DB:
    
    #-------------------------------------------------------------------------------------
    # Initializing class
    def __init__(self, sTime = None, sFileName = None, oVarInfo = None, oParamsInfo = None):
        
        # Check Database name
        if oParamsInfo['DB']['ID'] == 'DB_UNKNOWN':
            
            # DB UNKNOWN
            GetException(' -----> WARNING: Database set DB_UNKNOWN: Nothing to do!', 2, 1)
            oLogStream.info( ' ------> SELECTED DATABASE: ' + str(oParamsInfo['DB']['ID']) )
            
        elif oParamsInfo['DB']['ID'] == 'DB_RegMarche':
            
            # DB RegMarche
            oLogStream.info( ' ------> SELECTED DATABASE: ' + str(oParamsInfo['DB']['ID']) )
            DB_RegMarche(sTime, sFileName, oVarInfo, oParamsInfo['DB'])
            
        else:
            # Error message
            GetException(' -----> ERROR: DB name not correctly set! Please check your settings file!',1,1)
    #--------------------------------------------------------------------------------
        
#-------------------------------------------------------------------------------------
    
#--------------------------------------------------------------------------------
# Class to use DB_RegMarche
class DB_RegMarche:

    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, sTimeStep, sFileName, oVarInfo, oDBInfo):
        
        self.sTimeStep = sTimeStep
        self.sFileName = sFileName
        self.oVarInfo = oVarInfo
        self.oDBInfo = oDBInfo
        
        self.iTimeStep = self.oVarInfo['VarTimeStep']
        self.sVarName = self.oVarInfo['VarOp']['Op_GetEx']['Name']

        # Get time
        self.getTime(); 
        
        # Get data
        self.getData();
        
        # Save data
        self.saveData();

    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to get time info
    def getTime(self):
        
        # Time step info
        sTimeStep = self.sTimeStep
        iTimeStep = self.iTimeStep
        
        # Time definition
        oTimeStep = datetime.datetime.strptime(sTimeStep,'%Y%m%d%H%M%S')

        oTimeStepTo = oTimeStep; sTimeStepTo = oTimeStepTo.strftime('%Y-%m-%dT%H:%M:%S.%f'); 
        sTimeStepTo = sTimeStepTo[:-3]; #sTimeSaveTo = oTimeStepTo.strftime('%Y%m%d%H%M')
        oTimeStepFrom = oTimeStep - datetime.timedelta(seconds = iTimeStep); sTimeStepFrom = oTimeStepFrom.strftime('%Y-%m-%dT%H:%M:%S.%f'); 
        sTimeStepFrom = sTimeStepFrom[:-3]; #sTimeSaveFrom = oTimeStepFrom.strftime('%Y%m%d%H%M')
        
        # Save time in global declaration
        self.sTimeStepFrom = sTimeStepFrom
        self.sTimeStepTo = sTimeStepTo
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to save data info
    def saveData(self):
        
        # Get information
        sFileName = self.sFileName
        a1oDBData = self.a1oDBData

        # Save data
        oFileDrv = Drv_Data_IO(sFileName, 'w')
        oFileDrv.oFileWorkspace.writeFileData(a1oDBData)
     
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to get data info
    def getData(self):
        
        # SQL library
        import pymssql
        
        # Define DB info
        sDBID = self.oDBInfo['ID']
        sDBUser = self.oDBInfo['User']
        sDBName = self.oDBInfo['Name']
        sDBPassword = self.oDBInfo['Password']
        sDBServer = self.oDBInfo['Server']
        
        # Define DB query
        sDBQuery = self.defineQuery_AUT(self.sVarName, self.sTimeStepFrom, self.sTimeStepTo)
        
        oLogStream.info( ' ------> GET DATA FROM ETG SOURCE ... ' )
        
        # Open DB connection
        oDBConnection = pymssql.connect(sDBServer, sDBUser, sDBPassword, sDBName)
        oDBCursor = oDBConnection.cursor()
        # Execute DB query
        oDBCursor.execute(sDBQuery)
        # Get all data
        a1oDBData_AUT = oDBCursor.fetchall(); iDBLen_AUT = len(a1oDBData_AUT)
        # Close DB connection
        oDBConnection.commit()
        
        oLogStream.info( ' ------> GET DATA FROM ETG SOURCE ... OK (DATA VALUES: ' + str(iDBLen_AUT))
        
        # If PP or TA must be extracted also non-automatic section(s) from db
        oLogStream.info( ' ------> GET DATA FROM OTHER SOURCE ... ' )
        if self.sVarName == 'PP' or self.sVarName == 'TA':
            
            # Define DB query
            if (self.sVarName == 'PP'):
                sDBQuery = self.defineQuery_MEC('Pr', self.sTimeStepFrom, self.sTimeStepTo)
            elif (self.sVarName == 'TA'):  
                sDBQuery = self.defineQuery_MEC('Tr', self.sTimeStepFrom, self.sTimeStepTo)
            else:
                sDBQuery = ''
            
            if sDBQuery:
                # Open DB connection
                oDBConnection = pymssql.connect(sDBServer, sDBUser, sDBPassword, sDBName)
                oDBCursor = oDBConnection.cursor()
                # Execute DB query
                oDBCursor.execute(sDBQuery)
                # Get all data
                a1oDBData_MEC = oDBCursor.fetchall(); iDBLen_MEC = len(a1oDBData_MEC)
                # Close DB connection
                oDBConnection.commit()
                oLogStream.info( ' ------> GET DATA FROM ETG SOURCE ... OK (DATA VALUES: ' + str(iDBLen_MEC) + ')')
                
            else:
            
                GetException(' -----> WARNING: DB OTHER SOURCE NULL! CHECK YOUR SETTINGS!', 2, 1)
                a1oDBData_MEC = []
            
        else:
            oLogStream.info( ' ------> GET DATA FROM OTHER SOURCE ... SKIPPED' )
            a1oDBData_MEC = []
        
        a1oDBData = a1oDBData_AUT + a1oDBData_MEC
        iDBLen = len(a1oDBData)
        oLogStream.info( ' ------> ETG + OTHER SOURCE = VALUES: ' + str(iDBLen))
        
        self.a1oDBData = a1oDBData
        
    #--------------------------------------------------------------------------------
   
    #--------------------------------------------------------------------------------
    # Method to define query db (MEC query)
    def defineQuery_MEC(self, sVarName, sTimeStepFrom, sTimeStepTo):
                
        sDBQuery_MEC  = "DECLARE @DataInizio DATETIME, @DataFine DATETIME "
        sDBQuery_MEC += "SET @DataInizio = '" + sTimeStepFrom + "' "
        sDBQuery_MEC += "SET @DataFine = '" + sTimeStepTo + "' "
        sDBQuery_MEC += "SELECT s.CodiceUnico AS CodiceSensore, st.CodiceUnico AS CodiceStazione, st.NomeAnnale AS NomeStazione, ds.ValoreValidato AS Pioggia_mm, "
        sDBQuery_MEC += "geo.LongCentesimale AS Lon, geo.LatCentesimale AS Lat, geo.Quota AS Zm, sito.Regione, sito.Provincia, sito.Comune, s.BacinoAnnale, "
        sDBQuery_MEC += "CONVERT(CHAR(19), @DataInizio, 126 ) AS DataInizio, "
        sDBQuery_MEC += "CONVERT(CHAR(19), @DataFine,   126 ) AS DataFine "
        sDBQuery_MEC += "FROM DatoSensore AS ds INNER JOIN Sensore AS s ON ds.Sensore = s.CodiceUnico "
        sDBQuery_MEC += "    INNER JOIN Stazione AS st ON s.Stazione = st.CodiceUnico "
        sDBQuery_MEC += "    INNER JOIN Georeferenza AS geo ON st.Posizione = geo.IDGeo "
        sDBQuery_MEC += "    INNER JOIN Sito ON st.SitoCollocazione = sito.IDSito "
        sDBQuery_MEC += "WHERE "
        sDBQuery_MEC += "    ( ( ds.Data BETWEEN @DataInizio AND @DataFine ) AND NOT( ds.Data=@DataInizio ) ) "
        sDBQuery_MEC += "    AND (s.TipoSensore= '" + sVarName + "' ) "
        sDBQuery_MEC += "    AND NOT( ds.ValoreValidato IS NULL ) " 
        sDBQuery_MEC += "    AND NOT( geo.GaussBoagaEst IS NULL ) "
        sDBQuery_MEC += "    AND NOT( geo.GaussBoagaNord IS NULL ) "
        sDBQuery_MEC += "    AND NOT( geo.Quota IS NULL ) "
        sDBQuery_MEC += "ORDER BY st.CodiceUnico, ds.Data ASC "

        return sDBQuery_MEC
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to define query db (AUT query)
    def defineQuery_AUT(self, sVarName, sTimeStepFrom, sTimeStepTo):
        
        sDBQuery_AUT  = "DECLARE @DataInizio DATETIME, @DataFine DATETIME "
        sDBQuery_AUT += "SET @DataInizio = '" + sTimeStepFrom + "' "
        sDBQuery_AUT += "SET @DataFine = '" + sTimeStepTo + "' "
        sDBQuery_AUT += "SELECT s.CodiceUnico AS CodiceSensore, st.CodiceUnico AS CodiceStazione, st.NomeAnnale AS NomeStazione, ds.DatoOrigine AS Pioggia_mm, "
        sDBQuery_AUT += "geo.LongCentesimale AS Lon, geo.LatCentesimale AS Lat, geo.Quota AS Zm, sito.Regione, sito.Provincia, sito.Comune, s.BacinoAnnale, "
        sDBQuery_AUT += "CONVERT(CHAR(19), @DataInizio, 126 ) AS DataInizio, "
        sDBQuery_AUT += "CONVERT(CHAR(19), @DataFine,   126 ) AS DataFine "
        sDBQuery_AUT += "FROM DatoSensore AS ds INNER JOIN Sensore AS s ON ds.Sensore = s.CodiceUnico "
        sDBQuery_AUT += "    INNER JOIN Stazione AS st ON s.Stazione = st.CodiceUnico "
        sDBQuery_AUT += "    INNER JOIN Georeferenza AS geo ON st.Posizione = geo.IDGeo "
        sDBQuery_AUT += "    INNER JOIN Sito ON st.SitoCollocazione = sito.IDSito "
        sDBQuery_AUT += "WHERE "
        sDBQuery_AUT += "    ( ( ds.Data BETWEEN @DataInizio AND @DataFine ) AND NOT( ds.Data=@DataInizio ) ) "
        sDBQuery_AUT += "    AND (s.TipoSensore='" + sVarName + "' ) "
        sDBQuery_AUT += "    AND NOT( ds.DatoOrigine IS NULL ) "
        sDBQuery_AUT += "    AND NOT( geo.GaussBoagaEst IS NULL ) "
        sDBQuery_AUT += "    AND NOT( geo.GaussBoagaNord IS NULL ) "
        sDBQuery_AUT += "    AND NOT( geo.Quota IS NULL ) "
        sDBQuery_AUT += "ORDER BY st.CodiceUnico, ds.Data ASC "
        
        return sDBQuery_AUT
        
    #--------------------------------------------------------------------------------
        
        
        
        
        
        
    
