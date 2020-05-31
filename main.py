# coding=utf-8
# ¡Importante!: 'sql_clause' con ORDER BY sólo es soportado por bases de datos, no por otro tipo de datos
# como dBASE o INFO tables. Para solucionarlo se han copiado los datos a una nueva tabla dentro de una nueva gdb.


import arcpy, os, re, createViewsFromTableModule, calculateModule
from datetime import datetime, timedelta

arcpy.env.overwriteOutput = True
# print "Inicio " + str(datetime.now().time())
mdb = "Interurbanos.mdb"
flag = False
while not flag:
    # path = input("Ubicacion de " + mdb + ": ")
    path = "C://SyK//03_CURSOR//data"
    arcpy.env.workspace = path
    if arcpy.Exists(mdb):
        flag = True
    else:
        print("Este directorio no contiene el mdb")

interurbanos = os.path.join(path, "Interurbanos.gdb")
if arcpy.Exists(interurbanos):
    arcpy.Delete_management(interurbanos)
arcpy.CreateFileGDB_management(path, "Interurbanos")
arcpy.TableToTable_conversion(os.path.join(mdb, "Stop_Times_seq0_Trips_Calendar"), interurbanos, "Stop_Times_seq0_Trips_Calendar")
table = arcpy.env.workspace = os.path.join(path, interurbanos, "Stop_Times_seq0_Trips_Calendar")

arcpy.AddField_management(table, "TIEMPO_AUX", "DATE")
arcpy.AddField_management(table, "FRECUENCIA", "FLOAT", field_scale=1)
arcpy.AddField_management(table, "TIEMPO", "TEXT")

calculateModule.calculateTimeText(table)
calculateModule.calculateFrequency(table)
arcpy.DeleteField_management(table, "TIEMPO_AUX")

# Se localizan los valores unicos de routeId
routeIdList = []
with arcpy.da.SearchCursor(table, '*') as s4Cursor:
    for s4Row in s4Cursor:
        found = ''
        m = re.search('\d{3}', s4Row[7])
        if m:
            found = m.group(0)
        routeIdList.append(s4Row[7][0] + "___" + found)

arcpy.env.workspace = interurbanos
uniqRouteIdList = set(routeIdList)
viewTable = createViewsFromTableModule.fillUniqRouteIdClass(table)
days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

# Se crean tantas tablas como routeId diferentes haya con TableToTable
# Cada una de las tablas solo contendra un valor de routeId
# Se localizan los valores max y min del campo TIEMPO de cada una de las tablas

for r in uniqRouteIdList:
    nameView = "routeID" + r + "_view"
    nameTable = "Route" + r
    exp = "route_id = \'" + r + "\'"
    arcpy.MakeTableView_management(table, nameView, exp)
    arcpy.TableToTable_conversion(nameView, interurbanos, nameTable)
    for d in days:
        nameViewDay = nameTable + d + "_view"
        for field in arcpy.ListFields(nameTable):
            if d == field.name:
                arcpy.MakeTableView_management(nameTable, nameViewDay, d + "= 1")
                freqList = []
                with arcpy.da.SearchCursor(nameViewDay, '*') as s2Cursor:
                    for s2Row in s2Cursor:
                        freqList.append(s2Row[24])
                uniqFreqList = set(freqList)
                for freq in uniqFreqList:
                    if freq is not None:
                        nameViewDayFreq = nameViewDay + str(freq) + "_view"
                        nameTableOut = r + d.capitalize() + str(freq)
                        exp2 = "FRECUENCIA = " + str(freq)
                        arcpy.MakeTableView_management(nameViewDay, nameViewDayFreq, exp2)
                        timeList = []
                        with arcpy.da.SearchCursor(nameViewDayFreq, '*') as s3Cursor:
                            for s3Row in s3Cursor:
                                timeList.append(s3Row[25])
                        maximo = max(timeList)
                        minimo = min(timeList)
                        exp3 = "TIEMPO <> \'" + maximo + "\' AND TIEMPO <> \'" + minimo + "\'"
                        arcpy.MakeTableView_management(nameViewDayFreq, nameTableOut, exp3)
# print "Fin " + str(datetime.now().time())