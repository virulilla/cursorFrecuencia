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

calculateModule.calculateFRECUENCIA(table)
calculateModule.calculateTIEMPOandCOD_ITIN(table)

codItinList = []
with arcpy.da.SearchCursor(table, '*') as cursor:
    for row in cursor:
        codItinList.append(row[26])

arcpy.env.workspace = interurbanos

# Se crean tantas tablas como routeId diferentes haya con TableToTable
# Cada una de las tablas solo contendra un valor de routeId
# Se localizan los valores max y min del campo TIEMPO de cada una de las tablas
days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
viewTable = []
viewTableDay = [[], [], [], []]
viewTableDayM_Th = []
viewTableDayFri = []
viewTableDaySat = []
viewTableDaySun = []
viewTableDayFreq = []
for itinerate in set(codItinList):
    del viewTable[:]
    del viewTableDayFri[:]
    del viewTableDayM_Th[:]
    del viewTableDaySat[:]
    del viewTableDaySun[:]
    exp = "COD_ITIN = \'" + itinerate + "\'"
    viewTable = createViewsFromTableModule.fillViewTableData(table, exp)
    for obj in viewTable:
        for day in days:
            if obj.saturday == 1:
                viewTableDaySat.append(obj)
            elif obj.sunday == 1:
                viewTableDaySun.append(obj)
            elif obj.monday == 1 or obj.tuesday == 1 or obj.wednesday == 1 or obj.thursday == 1:
                viewTableDayM_Th.append(obj)
            elif obj.friday == 1:
                viewTableDayFri.append(obj)
    viewTableDay[0] = viewTableDaySat
    viewTableDay[1] = viewTableDaySun
    viewTableDay[2] = viewTableDayM_Th
    viewTableDay[3] = viewTableDayFri

    print itinerate
    for obj2 in viewTableDay:
        lineaFichero = []
        lineaFichero.append(itinerate)
        freqList = []
        for obj3 in obj2:
            freqList.append(obj3.FRECUENCIA)

        for freq in set(freqList):
            timeList = []
            if freq is not None:
                for obj4 in obj2:
                    if freq == obj4.FRECUENCIA:
                        timeList.append(obj4.TIEMPO)
                maximo = max(timeList)
                minimo = min(timeList)
                lineaFichero.append(minimo[:-2] + maximo[:-2])
                lineaFichero.append(freq)

print "Fin " + str(datetime.now().time())




# exp3 = "TIEMPO <> \'" + maximo + "\' AND TIEMPO <> \'" + minimo + "\'"
