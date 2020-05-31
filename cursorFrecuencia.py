# coding=utf-8
# ¡Importante!: 'sql_clause' con ORDER BY sólo es soportado por bases de datos, no por otro tipo de datos
# como dBASE o INFO tables. Para solucionarlo se han copiado los datos a una nueva tabla dentro de una nueva gdb.


import arcpy, os, re, uniqRouteIdClassModule
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

# Se convierten las horas en tipo de dato fecha
with arcpy.da.UpdateCursor(table, '*') as cursor:
    for row in cursor:
        row[24] = datetime.strptime(row[2], '%H:%M:%S') + timedelta(hours=2)
        cursor.updateRow(row)

# El contador i recorre tiempoList[]
# El contador j recorre deltaTimeList[]
# tiempoList[] contiene las horas
# deltaTimeList contiene las frecuencias
# Se crea una lista que almacena las horas para hacer la diferencia entre filas contiguas
tiempoList = []
deltaTimeList = []
i = 1
j = 0
with arcpy.da.SearchCursor(table, '*', sql_clause=(None, "ORDER BY trip_id, arrival_time")) as sCursor:
    for sRow in sCursor:
        tiempoList.append(sRow[24])

# Se calculan las frecuencias mediante una diferencia entre la lista tiempoList[] y el cursor uCursor.
# El resultado se alamacena en la lista deltaTimeList = []. Los datos de esta lista que son de tipo 'deltatime',
# se convierten a dato de tipo flotante, los cuales corresponden a minutos.
# En caso de que la diferencia sea positiva, el valor se introduce en el campo FRECUENCIA
# En caso de que la diferencia sea negativa significa que el cursor se encuentra en una fila que corresponde al dia
# siguiente, por tanto el valor queda como None
# Se almacena en el campo TIEMPO la hora como tipo de dato Texto
# Se almacena en el campo COD_ITIN el código del itinerario
with arcpy.da.UpdateCursor(table, '*', sql_clause=(None, "ORDER BY trip_id, arrival_time")) as uCursor:
    for uRow in uCursor:
        if i < len(tiempoList):
            deltaTimeList.append(round((tiempoList[i] - uRow[24]).total_seconds() / 60))
            if deltaTimeList[j] > 0:
                uRow[25] = deltaTimeList[j]
            else:
                uRow[25] = None
            uRow[26] = uRow[24].strftime('%Y/%m/%d %H:%M:%S')[11:].translate(None, ':')
            uCursor.updateRow(uRow)
            i += 1
            j += 1
arcpy.DeleteField_management(table, "TIEMPO_AUX")

# Se localizan los valores unicos de frecuencia
# freqList = []
# with arcpy.da.SearchCursor(table, '*') as s2Cursor:
#     for s2Row in s2Cursor:
#         freqList.append(s2Row[24])
# uniqFreqList = set(freqList)

# Se localizan los valores unicos de routeId
routeIdList = []
with arcpy.da.SearchCursor(table, '*') as s4Cursor:
    for s4Row in s4Cursor:
        found = ''
        m = re.search('\d{3}', s4Row[7])
        if m:
            found = m.group(0)
        routeIdList.append(s4Row[7][0] + "___" + found)
uniqRouteIdList = set(routeIdList)

arcpy.env.workspace = interurbanos
# Se crean tantas tablas como frecuencias diferentes haya con TableToTable
# Cada una de las tablas solo contendra un valor de frecuencia
# Se localizan los valores max y min del campo TIEMPO de cada una de las tablas
# for n in uniqFreqList:
#     tiempoUniqFrecList = []
#     if n is not None:
#         nameNewTable = "frec" + str(n)[:len(str(n)) - 2]
#         arcpy.MakeTableView_management(table, "tableView", "FRECUENCIA = " + str(n))
#         arcpy.TableToTable_conversion("tableView", interurbanos, nameNewTable)
#         with arcpy.da.SearchCursor("tableView", '*') as s3Cursor:
#             for s3Row in s3Cursor:
#                 tiempoUniqFrecList.append(s3Row[25])
#         maximo = max(tiempoUniqFrecList)
#         minimo = min(tiempoUniqFrecList)
#         exp = "TIEMPO <> \'" + maximo + "\' AND TIEMPO <> \'" + minimo + "\'"
#         arcpy.MakeTableView_management(nameNewTable, "tableViewDelete", exp)
#         arcpy.DeleteRows_management("tableViewDelete")


x = uniqRouteIdClassModule.rellenaUniqRouteIdClass(table)

# Se crean tantas tablas como routeId diferentes haya con TableToTable
# Cada una de las tablas solo contendra un valor de routeId
# Se localizan los valores max y min del campo TIEMPO de cada una de las tablas

days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

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