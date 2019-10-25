"""
	@author: Chris Buscaglia -- modified by Justin VanVleet, Greg Whitaker
	@contact: cbuscaglia@esri.com; justin.vanvleet@ihsmarkit.com; greg.whitaker@ihsmarkit.com
	@company: Esri, IHS Markit
	@version: 3.0
	@description: Publish CADNSDI
	@requirements: Python 2.7.x, ArcGIS 10.2, 10.3, 10.3.1, 10.4
	@copyright: Esri, 2015

	This tool is a modified version of the original parcel fabric publication tool published by ESRI.
	It has been enhanced to better fit the updated CadNSDI standard as well as provide additional functionality.
"""

# Import modules
import arcpy
from pds_utlities import rows_as_update_dicts

def main(OutputGdb, SelectXml, ParcelFabric, PointOutput, CalcXY, ControlOutput, Boolean, UserField):

	# Derive workspace, dataset, parcels, and points - added by GW 11/01/2017
	SplitParcelFabricPath = ParcelFabric.split('\\')
	ParcelFabricWorkspace = '\\'.join(SplitParcelFabricPath[:-2])
	ParcelFabricParcels = """{}_Parcels""".format(ParcelFabric)
	ParcelFabricPoints = """{}_Points""".format(ParcelFabric)
	ParcelFabricControl = """{}_Control""".format(ParcelFabric)
	CADNSDIFeatureDataset = """{}\\CadastralReference""".format(OutputGdb)

	MeanderedWater = """{}\\MeanderedWater""".format(CADNSDIFeatureDataset)
	PLSSIntersected = """{}\\PLSSIntersected""".format(CADNSDIFeatureDataset)
	PLSSFirstDivision = """{}\\PLSSFirstDivision""".format(CADNSDIFeatureDataset)
	PLSSSecondDivision = """{}\\PLSSSecondDivision""".format(CADNSDIFeatureDataset)
	PLSSSpecialSurvey = """{}\\PLSSSpecialSurvey""".format(CADNSDIFeatureDataset)
	PLSSTownship = """{}\\PLSSTownship""".format(CADNSDIFeatureDataset)
	PLSSPoint = """{}\\PLSSPoint""".format(CADNSDIFeatureDataset)
	MetadataGlance = """{}\\MetadataGlance""".format(CADNSDIFeatureDataset)
	ConflictedAreas = """{}\\ConflictedAreas""".format(CADNSDIFeatureDataset)
	Control = """{}\\Control""".format(CADNSDIFeatureDataset)


	# Create output workspace, import schema - added by GW 11/01/2017
	CreateOutGdbXml(OutputGdb, SelectXml)

	# Conditionally replaces RevisedDate values - added by GW 11/01/2017
	if Boolean == 'true':
		ReplaceRevisedDate(ParcelFabricWorkspace, ParcelFabricParcels, UserField)

	# Export the Parcel Fabric Layers - modified by GW 12/14/2017
	arcpy.AddMessage("Step 1: Exporting Layers by Type")

	# Create layers by type - modified by GW 12/14/2017
    # Added points selection to exclude non-PLSS points JV 2/23/2018

	if PointOutput == 'false':
		Points_query = "POINTID IS NOT NULL"
	else:
		Points_query = ""
	arcpy.MakeFeatureLayer_management(ParcelFabricPoints, 'Points_lyr', Points_query)

	arcpy.MakeFeatureLayer_management(ParcelFabricControl, 'Control_lyr')

	MeanderedWater_query = "SystemEndDate IS NULL AND Type = 4 AND SpecialSurveyType = 'Meandered Water'"
	arcpy.MakeFeatureLayer_management(ParcelFabricParcels, 'MeanderedWater_lyr', MeanderedWater_query)

	PLSSFirstDivision_query = "SystemEndDate is NULL AND Type = 2"
	arcpy.MakeFeatureLayer_management(ParcelFabricParcels, 'PLSSFirstDivision_lyr', PLSSFirstDivision_query)

	PLSSSecondDivision_query = "SystemEndDate is NULL AND Type = 12"
	arcpy.MakeFeatureLayer_management(ParcelFabricParcels, 'PLSSSecondDivision_lyr', PLSSSecondDivision_query)

	PLSSSpecialSurvey_query = "SystemEndDate is NULL AND Type = 4 AND (SpecialSurveyType <> 'Meandered Water' OR SpecialSurveyType IS NULL)"
	arcpy.MakeFeatureLayer_management(ParcelFabricParcels, 'PLSSSpecialSurvey_lyr', PLSSSpecialSurvey_query)

	PLSSTownship_query = "SystemEndDate  is NULL AND Type = 1 AND PLSSID is not NULL"
	arcpy.MakeFeatureLayer_management(ParcelFabricParcels, 'PLSSTownship_lyr',  PLSSTownship_query)

	ConflictedAreas_query = "ConflictCode = 'C'"
	arcpy.MakeFeatureLayer_management(ParcelFabricParcels, 'ConflictedAreas_lyr', ConflictedAreas_query)

	# Do the main things  - modified by GW 12/14/2017
	PointLoader('Points_lyr', PLSSPoint, CalcXY)
	MeanderdWaterLoader('MeanderedWater_lyr', MeanderedWater)
	FirstDivisionLoader('PLSSFirstDivision_lyr', PLSSFirstDivision)
	CalculateFirstDivTypeCodes(PLSSFirstDivision)
	SecondDivisionLoader('PLSSSecondDivision_lyr', PLSSSecondDivision)
	CalculateSecDivTypeCodes(PLSSSecondDivision)
	SpecialSurveyLoader( 'PLSSSpecialSurvey_lyr', PLSSSpecialSurvey)
	CalculateSpecialSurveyTypeCodes(PLSSSpecialSurvey)
	TownshipLoader('PLSSTownship_lyr', PLSSTownship)
	CalculateMeridianValues(PLSSTownship)
	MetadataGlanceLoader('PLSSTownship_lyr', MetadataGlance)
	ConflictedAreasLoader('ConflictedAreas_lyr', ConflictedAreas)
	ControlLoader('Control_lyr', Control, ControlOutput)

	arcpy.Delete_management(PLSSIntersected)


	# reproject special case states - added by GW 11/01/2017
	if SelectXml in ['Montana', 'Ohio', 'Wisconsin', 'California']:
		ReprojectHARNDataset(OutputGdb,CalcXY)

	# remind user to re-enable editor tracking - added by GW 11/01/2017
	if Boolean == 'true':
		arcpy.AddWarning('\n!!! Editor Tracking has been disabled. Please re-enable Editor Tracking now. !!!\n')


# Added by GW 11/01/2017 to automate xml/output gdb creation
def CreateOutGdbXml(OutputGdb, SelectXml):
	arcpy.AddMessage("\nPreliminary Step: Creating output geodatabase, importing schema definition")

	# create separate objects from user supplied path
	SplitGdbPath = OutputGdb.split('\\')
	Folder = '\\'.join(SplitGdbPath[:-1])
	GdbName = '\\'.join(SplitGdbPath[-1:])

	# store xml paths as dictionary values, retrieve user selected
	XmlPaths = {'Standard' : '..\\Parcel_Fabric_Publication_Premier_V3.1_BETA\\XML_CADNSDI_WITH_AREA_IN_1STDIV.xml',
				'Montana' : '..\\Parcel_Fabric_Publication_Premier_V3.1_BETA\\XML_CADNSDI_MONTANA_HARN.xml',
				'Ohio' : '..\\Parcel_Fabric_Publication_Premier_V3.1_BETA\\XML_Ohio.xml',
				'Wisconsin' : '..\\Parcel_Fabric_Publication_Premier_V3.1_BETA\\XML_CADNSDI_WISCONSIN_HARN.xml',
				'California' : '..\\Parcel_Fabric_Publication_Premier_V3.1_BETA\\XML_CADNSDI_CALIFORNIA_TEAL_ALBERS.xml'}

	# create the gdb and import selected xml
	arcpy.CreateFileGDB_management(Folder, GdbName, 'CURRENT')
	arcpy.ImportXMLWorkspaceDocument_management(OutputGdb, XmlPaths[SelectXml], 'SCHEMA_ONLY')



# Added by GW 11/01/2017 to automate conditional reporojection of HARN datasets (Added other custom projections--not just Harn. JV)
def ReprojectHARNDataset(OutputGdb, CalcXY):
	arcpy.AddMessage("\nFinal Step: Reprojecting dataset to NAD 1983")

	# create separate objects from user supplied path
	SplitGdbPath = OutputGdb.split('\\')
	Folder = '\\'.join(SplitGdbPath[:-1])
	GdbName = '\\'.join(SplitGdbPath[-1:]).split('.')[0]
	GdbNameNAD83 = GdbName + '_NAD83.gdb'
	OutputGdbNAD83 = Folder + '\\' + GdbNameNAD83

	# create spatial reference object, new gdb, new feature dataset
	sr = arcpy.SpatialReference('NAD 1983')
	arcpy.CreateFileGDB_management(Folder, GdbNameNAD83, 'CURRENT')
	arcpy.CreateFeatureDataset_management(OutputGdbNAD83, 'CadastralReference', sr)

	# input/outut, import HARN features into NAD83 dataset
	infcs = ["""{}\\CadastralReference\\PLSSTownship""".format(OutputGdb),
			 """{}\\CadastralReference\\PLSSSpecialSurvey""".format(OutputGdb),
			 """{}\\CadastralReference\\PLSSSecondDivision""".format(OutputGdb),
			 """{}\\CadastralReference\\PLSSPoint""".format(OutputGdb),
			 """{}\\CadastralReference\\PLSSFirstDivision""".format(OutputGdb),
			 """{}\\CadastralReference\\MetadataGlance""".format(OutputGdb),
			 """{}\\CadastralReference\\MeanderedWater""".format(OutputGdb),
			 """{}\\CadastralReference\\ConflictedAreas""".format(OutputGdb),
			 """{}\\CadastralReference\\Control""".format(OutputGdb),
			 """{}\\CadastralReference\\SurveySystem""".format(OutputGdb)]

	outdataset = """{}\\CadastralReference""".format(OutputGdbNAD83)
	arcpy.FeatureClassToGeodatabase_conversion(infcs, outdataset)

	PLSSPointReProject = """{}\\PLSSPoint""".format(outdataset)
	
	if CalcXY == 'true':
		arcpy.AddMessage("Calculating XCOORD, YCOORD, COORDSYS AND HDATUM")
		arcpy.CalculateField_management(PLSSPointReProject, "XCOORD", "!Shape.Centroid.X!", "Python_9.3", "")
		arcpy.CalculateField_management(PLSSPointReProject, "YCOORD", "!Shape.Centroid.Y!", "Python_9.3", "")
		spatialRef = arcpy.Describe(PLSSPointReProject).SpatialReference
		srType = "'{}'".format(spatialRef.type)
		#srName = "'{}'".format(spatialRef.name) Possibly to be used later. Right now the HDATUM is hard coded to NAD83 to fit the CadNSDI standard.
		arcpy.CalculateField_management(PLSSPointReProject, "COORDSYS", srType, "PYTHON", "")
		arcpy.CalculateField_management(PLSSPointReProject, "HDATUM", "'NAD83'", "PYTHON", "")


# Added by GW 11/01/2017 to replace RevisedDate with Modify date
def ReplaceRevisedDate(ParcelFabricWorkspace, ParcelFabricParcels, UserField):
	arcpy.AddMessage("\nPreliminary Step: Disabling Editor Tracking and Updating RevisedDate Values")

	# disable editor tracking to ensure system doesn't track date updates
	arcpy.DisableEditorTracking_management(ParcelFabricParcels)

	# start edit session
	edit = arcpy.da.Editor(ParcelFabricWorkspace)
	edit.startEditing()
	edit.startOperation()

	# use update cursor to find, evaluate, and update values
	fields = ['REVISEDDATE', UserField]
	if UserField <> '':
		with arcpy.da.UpdateCursor(ParcelFabricParcels, fields) as updateRows:
			for updateRow in updateRows:
				if (updateRow[0] <> None) and (updateRow[0] < updateRow[1]):
					updateRow[0] = str(updateRow[1]).split(' ')[0]
					updateRows.updateRow(updateRow)
	else:
		arcpy.AddWarning("     --No replacement field selected. Skipping RevisedDate updates.")

	# end edit session & save
	edit.stopOperation()
	edit.stopEditing(True) #True=save


# Publish control box if checked
def ControlLoader(Control1, Control, ControlOutput):
	if ControlOutput == 'true':
		arcpy.AddMessage("Processing Control Points")
		arcpy.Append_management(Control1, Control, "NO_TEST", "", "")
	#else:
		#arcpy.Delete_management(Control)


# Field Map the PLSSPoint Feature Class
def PointLoader(PLSSPoint1, PLSSPoint, CalcXY):
		PLSSPointHelper = """
		PLSSID \"Township Identifier\" true true false 16 Text 0 0 ,First,#,{0},PLSSID,-1,-1;
		PLSSID \"Township Identifier\" true true false 16 Text 0 0 ,First,#,{0},PLSSID,-1,-1;
		POINTID \"Corner Point ID\" true true false 25 Text 0 0 ,First,#,{0},POINTID,-1,-1;
		POINTLAB \"Corner Point Label\" true true false 25 Text 0 0 ,First,#,{0},POINTLAB,-1,-1;
		XCOORD \"X or East Coordinate\" true true false 8 Double 0 0 ,First,#,{0},XCOORD,-1,-1;
		YCOORD \"Y or North Coordinate\" true true false 8 Double 0 0 ,First,#,{0},YCOORD,-1,-1;
		ZCOORD \"Z or Height Coordinate\" true true false 8 Double 0 0 ,First,#,{0},Z,-1,-1;
		ELEV \"Average Township Elevation\" true true false 8 Double 0 0 ,First,#,{0},ELEV,-1,-1;
		RELYTXT \"Reliability Text\" true true false 25 Text 0 0 ,First,#,{0},RELYTXT,-1,-1;
		RELYNUMB \"Reliability Number\" true true false 8 Double 0 0 ,First,#,{0},RELYNUMB,-1,-1;
		ERRORX \"Error in X\" true true false 8 Double 0 0 ,First,#,{0},ERRORX,-1,-1;
		ERRORY \"Error in Y\" true true false 8 Double 0 0 ,First,#,{0},ERRORY,-1,-1;
		ERRORZ \"Error in Z\" true true false 8 Double 0 0 ,First,#,{0},ERRORZ,-1,-1;
		HDATUM \"Horizontal Datum\" true true false 20 Text 0 0 ,First,#,{0},HDATUM,-1,-1;
		VDATUM \"Vertical Datum\" true true false 20 Text 0 0 ,First,#,{0},VDATUM,-1,-1;
		COORDMETH \"Coordinate Collection Method\" true true false 25 Text 0 0 ,First,#,{0},COORDMETH,-1,-1;
		COORDSYS \"Coordinate System\" true true false 50 Text 0 0 ,First,#,{0},COORDSYS,-1,-1;
		STEWARD1 \"Data Steward\" true true false 50 Text 0 0 ,First,#,{0},STEWARD1,-1,-1;
		STEWARD2 \"Second Data Steward\" true true false 50 Text 0 0 ,First,#,{0},STEWARD2,-1,-1;
		LOCAL1 \"First PLSS Point Alternate Name\" true true false 25 Text 0 0 ,First,#,{0},LOCAL1,-1,-1;
		LOCAL2 \"Second PLSS Point Alternate Name\" true true false 25 Text 0 0 ,First,#,{0},LOCAL2,-1,-1;
		LOCAL3 \"Third PLSS Point Alternate Name\" true true false 25 Text 0 0 ,First,#,{0},LOCAL3,-1,-1;
		LOCAL4 \"Fourth PLSS Point Alternate Name\" true true false 25 Text 0 0 ,First,#,{0},LOCAL4,-1,-1;
		SURVEYYEAR \"Survey Year\" true true false 4 Long 0 0 ,First,#,{0},SURVEYYEAR,-1,-1;
		REVISEDDATE \"Revised Date\" true true false 8 Date 0 0 ,First,#,{0},REVISEDDATE,-1,-1""".format(PLSSPoint1)

		#Append points and calculate spatial reference fields
		arcpy.AddMessage("Step 2: Processing PLSS Points")
		arcpy.Append_management(PLSSPoint1, PLSSPoint, "NO_TEST", PLSSPointHelper, "")
		if CalcXY == 'true':
			arcpy.AddMessage("Calculating XCOORD, YCOORD, COORDSYS AND HDATUM")
			arcpy.CalculateField_management(PLSSPoint, "XCOORD", "!Shape.Centroid.X!", "Python_9.3", "")
			arcpy.CalculateField_management(PLSSPoint, "YCOORD", "!Shape.Centroid.Y!", "Python_9.3", "")
			spatialRef = arcpy.Describe(PLSSPoint).SpatialReference
			srType = "'{}'".format(spatialRef.type)
			#srName = "'{}'".format(spatialRef.name) Possibly to be used later. Right now the HDATUM is hard coded to NAD83 to fit the CadNSDI standard.
			arcpy.CalculateField_management(PLSSPoint, "COORDSYS", srType, "PYTHON", "")
			arcpy.CalculateField_management(PLSSPoint, "HDATUM", "'NAD83'", "PYTHON", "")



# Field Map the Meandered Water Feature Class
def MeanderdWaterLoader(MeanderedWater1, MeanderedWater):
		MeanderedWater1Helper = """
		SURVTYP \"Survey Type Code\" true true false 2 Text 0 0 ,First,#;
		SURVTYPTXT \"Survey Type Text\" true true false 50 Text 0 0 ,First,#,{0},SpecialSurveyType,-1,-1;
		SHAPE_Length \"SHAPE_Length\" false true true 8 Double 0 0 ,First,#,{0},Shape_Length,-1,-1;
		SHAPE_Area \"SHAPE_Area\" false true true 8 Double 0 0 ,First,#,{0},Shape_Area,-1,-1""".format(MeanderedWater1)

		arcpy.AddMessage("Step 3: Processing Meandered Water")
		arcpy.Append_management(MeanderedWater1, MeanderedWater, "NO_TEST", MeanderedWater1Helper, "")

		# Calculate the SURVTYP code
		try:
			arcpy.CalculateField_management(MeanderedWater, "SURVTYP", "'W'", "PYTHON", "")
		except:
			arcpy.AddWarning("!!! Error calculating SURVTYP !!!")


# Field Map the First Division Feature Class - Modified by GW 11/01/2017
def FirstDivisionLoader(PLSSFirst1, PLSSFirstDivision):
		FirstDivHelper = """
		FRSTDIVID \"First Division Identifier\" true true false 22 Text 0 0 , First,#,{0},PLSSID,-1,-1;
		FRSTDIVID \"First Division Identifier\" true true false 22 Text 0 0 , First,#,{0},PLSSID,-1,-1;
		FRSTDIVTXT \"First Division Type Text\" true true false 50 Text 0 0 , First,#, {0},FirstDivisionType, -1, -1;
		FRSTDIVNO \"First Division Number\" true true false 10 Text 0 0 , First,#, {0}, Name,-1, -1;
		FRSTDIVDUP \"First Division Duplicate\" true true false 1 Text 0 0 , First,#,{0},FirstDivisionDupCode,-1,-1;
		FRSTDIVLAB \"First Division Label\" true true false 20 Text 0 0 , First,#, {0}, Name,-1, -1;
		SURVTYPTXT \"Survey Type Text\" true true false 50 Text 0 0 ,First,#,{0},SpecialSurveyType,-1,-1;
		RECRDAREATX \"Record Area Text\" true true false 20 Text 0 0 ,First,#,{0},RECRDAREATX,-1,-1;
		RECRDAREANO \"Record Area Number\" true true false 8 Double 0 0 ,First,#,{0},RECRDAREANO,-1,-1;
		SOURCEDATE \"Source Doc Date\" true true false 8 Date 0 0 , First,#,{0},SOURCEDATE;
		SOURCEREF \"Source Doc Link or Reference\" true true false 100 Text 0 0 ,First,#,{0},SOURCEREF,-1,-1""".format(PLSSFirst1)

		#Append and Calculate First Division Fields
		arcpy.AddMessage("Step 4: Processing First Divisions")
		arcpy.Append_management(PLSSFirst1, PLSSFirstDivision, "NO_TEST", FirstDivHelper, "")

		FRSTPLSSIDHelper = "!FRSTDIVID![:15]"
		arcpy.CalculateField_management(PLSSFirstDivision, "PLSSID", FRSTPLSSIDHelper, "PYTHON", "")

		arcpy.CalculateField_management(PLSSFirstDivision, "GISACRE", "!SHAPE.area@ACRES!", "PYTHON", "")


# Modified by GW 11/01/2017 to include exception handling
def CalculateFirstDivTypeCodes(PLSSFirstDivision):
	FirstDivCodeBlock = """
def firstDivCodeBlock(firstDivText):
	if firstDivText == "Section":
		return "SN"
	if firstDivText == "Unsurveyed Unprotracted":
		return "UN"
	if firstDivText == "Unsurveyed Protracted":
		return "UP"
	if firstDivText == "Protracted Block":
		return "PB"
	if firstDivText == "Protraction Block":
		return "PB"
	if firstDivText == "Tract":
		return "TR"
	if firstDivText == "Quarter Township":
		return "QT"
	if firstDivText == "Lot":
		return "LT"
	if firstDivText == "Fractional Section":
		return "FS"
	if firstDivText == "Unsectionalized Area":
		return "UA"
	if firstDivText == "Other":
		return "UK"
	if firstDivText == "Unknown":
		return "UA"

	"""

	try:
		arcpy.AddMessage("     --Calculating First Division Type Codes")
		arcpy.CalculateField_management(PLSSFirstDivision, "FRSTDIVTYP", "firstDivCodeBlock(!FRSTDIVTXT!)", "PYTHON", FirstDivCodeBlock)
	except:
		arcpy.AddWarning("!!! Error calculating FRSTDIVTYP. Check for invalid values in the FRSTDIVTXT field !!!")


# Field Map the Second Division Feature Class - Modified by GW 11/01/2017 -- Modified by JV/GW 12/14/17 Eliminated PLSSID and FIRSDIVID calculations
def SecondDivisionLoader(PLSSSecond1, PLSSSecondDivision):
		SecondDivHelper = """
		SECDIVID \"Second Division Identifier\" true true false 50 Text 0 0 ,First,#,{0},PLSSID,-1,-1;
		SECDIVID \"Second Division Identifier\" true true false 50 Text 0 0 ,First,#,{0},PLSSID,-1,-1;
		FRSTDIVID \"First Division Identifier\" true true false 22 Text 0 0 ,First,#,{0},PLSSID,0,19;
		PLSSID \"Township Identifier\" true true false 16 Text 0 0 ,First,#,{0},PLSSID,0,14;
		SECDIVTYP \"Second Division Type Code\" true true false 1 Text 0 0 ,First,#;
		SECDIVTXT \"Second Division Type Text\" true false false 50 Text 0 0 ,First,#,{0},SecondDivisionType,-1,-1;
		SECDIVNO \"Second Division Number\" true true false 50 Text 0 0 ,First,#,{0},SecondDivisionNumber,-1,-1;
		SECDIVSUF \"Second Division Suffix\" true true false 10 Text 0 0 ,First,#,{0},SecondDivisionSuffix,-1,-1;
		SECDIVNOTE \"Second Division Note\" true true false 50 Text 0 0 ,First,#,{0},SpecialSurveyNotes,-1,-1;
		SECDIVLAB \"Second Division Label\" true true false 50 Text 0 0 ,First,#,{0},Name,-1,-1;
		SURVTYPTXT \"Survey Type Text\" true true false 50 Text 0 0 ,First,#,{0},SpecialSurveyType,-1,-1;
		SOURCEDATE \"Source Doc Date\" true true false 8 Date 0 0 ,First,#,{0},SOURCEDATE,-1,-1;
		SOURCEREF \"Source Doc Link or Reference\" true true false 100 Text 0 0 ,First,#,{0},SOURCEREF,-1,-1;
		RECRDAREATX \"Record Area Text\" true true false 20 Text 0 0 ,First,#,{0},RECRDAREATX,-1,-1;
		RECRDAREANO \"Record Area Number\" true true false 8 Double 0 0 ,First,#,{0},RECRDAREANO,-1,-1;
		GISACRE \"GIS Area Acre\" true true false 8 Double 0 0 ,First,#""".format(PLSSSecond1)

		#Append and Calculate Second Division fields
		arcpy.AddMessage("Step 5: Processing Second Divisions")
		arcpy.Append_management(PLSSSecond1, PLSSSecondDivision, "NO_TEST", SecondDivHelper, "")

		arcpy.CalculateField_management(PLSSSecondDivision, "GISACRE", "!SHAPE.area@ACRES!", "PYTHON", "")

		#Leave only the lot number for lots in SECDIVNO
		arcpy.CalculateField_management(PLSSSecondDivision, "SECDIVNO", "!SECDIVNO!.strip('L').strip()", "PYTHON")


def CalculateSecDivTypeCodes(PLSSSecondDivision):
	SecDivCodeBlock = """
def secDivCodeBlock(secDivText):
	if secDivText == "Aliquot Part" or secDivText == "Sixteenth":
		return "A"
	if secDivText == "Remainder Aliquot Part" or secDivText == "Other Aliquot Part":
		return "B"
	if secDivText == "Government Lot" or secDivText == "Lot":
		return "L"
	if secDivText == "Unnumbered Lot":
		return "O"
	if secDivText == "Unsurveyed" or secDivText == "Unsurveyed Protracted" or secDivText == "Protracted Lot":
		return "U"
	if secDivText == "Unsuveyed Unprotracted":
		return "Z"
	if secDivText == "Quarter Section":
		return "Q"
	if secDivText == "Remainder Lot":
		return "V"
	"""

	try:
		arcpy.AddMessage("     --Calculating Second Division Type Codes")
		arcpy.CalculateField_management(PLSSSecondDivision, "SECDIVTYP", "secDivCodeBlock(!SECDIVTXT!)", "PYTHON", SecDivCodeBlock)
	except:
		arcpy.AddWarning("!!! Error calculating SECDIVTYP. Check for invalid values in the SECDIVTXT field !!!")


# Field Map the Special Survey Feature Class	 - Modified by GW 11/01/2017
def SpecialSurveyLoader(PLSSSpecial1, PLSSSpecialSurvey):
		SpecialSurveyHelper = """
		SURVID \"Survey Identifier\" true true false 50 Text 0 0 , First,#,{0},PLSSID,-1,-1;
		SURVID \"Survey Identifier\" true true false 50 Text 0 0 , First,#,{0},PLSSID,-1,-1;
		SURVTYP \"Survey Type Code\" true true false 2 Text 0 0 , First,#;
		SURVTYPTXT \"Survey Type Text\" true true false 50 Text 0 0 ,First,#,{0},SpecialSurveyType,-1,-1;
		SURVNO \"Survey Number\" true true false 50 Text 0 0 , First,#,{0},SpecialSurveyNumber,-1,-1;
		SURVSUF \"Survey Suffix\" true true false 5 Text 0 0 , First,#,{0},SpecialSurveySuffix,-1,-1;
		SURVNOTE \"Survey Note\" true true false 50 Text 0 0 , First,#,{0},SpecialSurveyNotes,-1,-1;
		SURVDIV \"Special Survey Division\" true true false 50 Text 0 0 , First,#,{0},SecondDivisionNumber,-1,-1;
		SURVLAB \"Survey Label\" true true false 50 Text 0 0 , First,#,{0},Name,-1,-1;
		RECRDAREATX \"Record Area Text\" true true false 20 Text 0 0 , First,#,{0},RECRDAREATX,-1,-1;
		RECRDAREANO \"Record Area Number\" true true false 8 Double 0 0 ,First,#,{0},RECRDAREANO,-1,-1;
		GISACRE \"GIS Area Acres\" true true false 8 Double 0 0 , First,#;
		SOURCEREF \"Source Doc Link or Reference\" true true false 100 Text 0 0 , First,#,{0},SOURCEREF,-1,-1;
		SOURCEDATE \"Source Doc Date\" true true false 8 Date 0 0 , First,#,{0},SOURCEDATE""".format(PLSSSpecial1)

		#Append and Calculate Second Division fields
		arcpy.AddMessage("Step 6: Processing Special Surveys")
		arcpy.Append_management(PLSSSpecial1, PLSSSpecialSurvey, "NO_TEST", SpecialSurveyHelper, "")

		arcpy.CalculateField_management(PLSSSpecialSurvey, "GISACRE", "!SHAPE.area@ACRES!", "PYTHON", "")


# Modified by GW 11/01/2017 to include L:'Lot' for WY, exception handling
def CalculateSpecialSurveyTypeCodes(PLSSSpecialSurvey):
	surveyCodes = {"P":"BLM Parcel",
				   "D":"Allotment Survey",
				   "E":"Metes and Bounds",
				   "F":"Farm Unit Survey",
				   "G":"Land Grant",
				   "H":"Homestead Entry",
				   "I":"Indian Interest",
				   "J":"Small Tract, Small Holding Claim",
				   "M":"Mineral Survey",
				   "N":"Townsite Survey",
				   "K":"Townsite Block",
				   "Y":"Townsite Outlot",
				   "Q":"Donation Land Claim",
				   "S":"United States Survey",
				   "T":"Tract",
				   "X":"Exchange Survey",
				   "U":"Unsurveyed Protracted",
				   "Z":"Unsurveyed Unprotracted",
				   "W":"Meandered Water",
				   "L":"Government Lot",
				   "L":"Lot",
				   "2":"Irrigation Block",
				   "3":"Irrigation Project",
				   "4":"Irrigation Districts",
				   "O":"Unnumbered Lot",
				   "A":"Aliquot Part",
				   "C":"Coal",
				   "R":"Private Land"}

	try:
		arcpy.AddMessage("     --Calculating Special Survey Type Codes")
		where_clause = "SURVTYPTXT is NOT NULL AND SURVTYPTXT NOT in ('Unsurveyed Protracted', '')"
		with arcpy.da.UpdateCursor(PLSSSpecialSurvey, ["SURVTYPTXT", "SURVTYP"], where_clause) as updateCursor:
			for survey in rows_as_update_dicts(updateCursor):
				if survey["SURVTYPTXT"] in surveyCodes.values():
					survey["SURVTYP"] = surveyCodes.keys()[surveyCodes.values().index(survey["SURVTYPTXT"])]
	except:
		arcpy.AddWarning("!!! Error calculating SURVTYP. Check for invalid values in the SURVTYPTXT field !!!")


# Field Map the Township Feature Class
def TownshipLoader(PLSSTownship1 , PLSSTownship):
		TownshipHelper = """
		TWNSHPNO \"Township Number\" true true false 3 Text 0 0 , First,#,{0},TownshipNumber,-1,-1;
		TWNSHPNO \"Township Number\" true true false 3 Text 0 0 , First,#,{0},TownshipNumber,-1,-1;
		PRINMER \"Principal Meridian\" true true false  Text 0 0 , First,#,{0},PrincipalMeridian,-1,-1;
		TWNSHPFRAC \"Township Fraction\" true true false 1 Text 0 0 , First,#,{0},TownshipFraction,-1,-1;
		TWNSHPDIR \"Township Direction\" true true false 1 Text 0 0 , First,#,{0},TownshipDirection,-1,-1;
		RANGENO \"Range Number\" true true false 3 Text 0 0 , First,#,{0},RangeNumber,-1,-1;
		RANGEFRAC \"Range Fraction\" true true false 1 Text 0 0 , First,#,{0},RangeFraction,-1,-1;
		RANGEDIR \"Range Direction\" true true false 1 Text 0 0 , First,#,{0},RangeDirection,-1,-1;
		TWNSHPDPCD \"Township Duplicate\" true true false 1 Text 0 0 , First,#,{0},TownshipDupCode,-1,-1;
		PLSSID \"Township Identifier\" true true false 16 Text 0 0 , First,#,{0}, PLSSID,-1,-1;
		TWNSHPLAB \"Township Label\" true true false 20 Text 0 0 , First,#,{0}, Name, -1, -1;
		SRVNAME \"Survey Name for PLSS Areas\" true true false 60 Text 0 0 , First,#,{0},SpecialSurveyNotes,-1,-1,{0},SpecialSurveyNumber,-1,-1;
		SURVTYPTXT \"Survey Type Text\" true true false 50 Text 0 0 , First,#,{0},SpecialSurveyNotes,-1,-1;
		SOURCEDATE \"Source Date\" true true false 8 Date 0 0 , First,#,{0},SOURCEDATE;
		SOURCEREF \"Source Doc Link or Reference\" true true false 100 Text 0 0 , First,#,{0},SOURCEREF,-1,-1""".format(PLSSTownship1)

		arcpy.AddMessage("Step 7: Processing Townships")
		arcpy.Append_management(PLSSTownship1, PLSSTownship, "NO_TEST", TownshipHelper, "")
		STATEABBRHelper = "!PLSSID![:2]"
		arcpy.CalculateField_management(PLSSTownship, "STATEABBR", STATEABBRHelper, "PYTHON", "")
		PRINMERCDHelper = "!PLSSID! [2:4]"
		arcpy.CalculateField_management(PLSSTownship, "PRINMERCD", PRINMERCDHelper, "PYTHON", "")


# Added by GW 11/01/2017 to get description from coded value domain
def CalculateMeridianValues(PLSSTownship):
	meridianCodes = {"01":"1st Meridian",
					 "02":"2nd Meridian",
					 "03":"3rd Meridian",
					 "04":"4th Meridian",
					 "05":"5th Meridian",
					 "06":"6th Meridian",
					 "07":"Black Hills Meridian",
					 "08":"Boise Meridian",
					 "09":"Chickasaw Meridian",
					 "10":"Choctaw Meridian",
					 "11":"Cimarron Meridian",
					 "12":"Copper River Meridian",
					 "13":"Fairbanks Meridian",
					 "14":"Gila-Salt River Meridian",
					 "15":"Humboldt Meridian",
					 "16":"Huntsville Meridian",
					 "17":"Indian Meridian",
					 "18":"Louisiana Meridian",
					 "19":"Michigan Meridian",
					 "20":"Montana Meridian",
					 "21":"Mount Diablo Meridian",
					 "22":"Navajo Meridian",
					 "23":"New Mexico Meridian",
					 "24":"St. Helena Meridian",
					 "25":"St. Stephens Meridian",
					 "26":"Salt Lake Meridian",
					 "27":"San Bernardino Meridian",
					 "28":"Seward Meridian",
					 "29":"Tallahassee Meridian",
					 "30":"Uintah Meridian",
					 "31":"Ute Meridian",
					 "32":"Washington Meridian",
					 "33":"Willamette Meridian",
					 "34":"Wind River Meridian",
					 "36":"Between the Miamis",
					 "37":"Muskingum River",
					 "39":"Scioto River (First)",
					 "40":"Scioto River (Second)",
					 "43":"Twelve Mile Square Reserve",
					 "44":"Kateel River Meridian",
					 "45":"Umiat Meridian",
					 "46":"Extended Fourth Meridian",
					 "47":"West of the Great Miami",
					 "48":"Base Line of the US Military Survey",
					 "91":"Connecticut Western Reserve",
					 "99":"Not Applicable"}

	try:
		arcpy.AddMessage("     --Calculating Meridian Values from Domain Codes")
		with arcpy.da.UpdateCursor(PLSSTownship, ["PRINMER", "PRINMERCD"]) as updateCursor:
			for meridian in rows_as_update_dicts(updateCursor):
				if meridian["PRINMERCD"] in meridianCodes.keys():
					meridian["PRINMER"] = meridianCodes.get(meridian["PRINMERCD"])
	except:
		arcpy.AddWarning("!!! Error calculating PRINMER. Check for invalid values in the PRINMERCD field !!!")


# Field Map the Metadata Glance Feature Class
def MetadataGlanceLoader(PLSSTownship1 , MetadataGlance):
		MetadataGlanceHelper = """
		PLSSID \"Township Identifier\" true true false 16 Text 0 0 , First,#,{0}, PLSSID,-1,-1;
		PLSSID \"Township Identifier\" true true false 16 Text 0 0 , First,#,{0}, PLSSID,-1,-1;
		TWNSHPLAB \"Township Label\" true true false 20 Text 0 0 , First,#,{0}, Name, -1, -1;
		REVISEDDATE \"Revised Date\" true true false 8 Date 0 0 , First,#,{0}, REVISEDDATE,-1,-1;
		STEWARD \"Township Identifier\" true true false 16 Text 0 0 , First,#,{0}, STEWARD,-1,-1""".format(PLSSTownship1)

		arcpy.AddMessage("Step 8: Processing MetadataGlance")
		arcpy.Append_management(PLSSTownship1, MetadataGlance, "NO_TEST", MetadataGlanceHelper, "")
		STATEABBRHelper = "!PLSSID![:2]"
		arcpy.CalculateField_management(MetadataGlance, "STATEABBR", STATEABBRHelper, "PYTHON", "")


# Added by GW 11/01/2017, export and field map ConflictedAreas feature class
def ConflictedAreasLoader(ConflictedAreas1 , ConflictedAreas):
		ConflictedAreasHelper = """
		COMMENT \"Comment on Conflicted Area\" true true false 50 Text 0 0 , First,#,{0}, ConflictDescr,-1,-1;
		STEWARD1 \"Data Steward\" true true false 50 Text 0 0 , First,#,{0}, STEWARD,-1,-1;
		STEWARD2 \"Second Data Steward\" true true false 50 Text 0 0 , First,#,{0}, STEWARD2,-1,-1""".format(ConflictedAreas1)

		#Append ConflictedArea features
		arcpy.AddMessage("Step 9: Processing ConflictedAreas")
		arcpy.Append_management(ConflictedAreas1, ConflictedAreas, "NO_TEST", ConflictedAreasHelper, "")


if __name__ == '__main__':
	argv = tuple(arcpy.GetParameterAsText(i)for i in range(arcpy.GetArgumentCount()))
	main(*argv)
