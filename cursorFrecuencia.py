# coding=utf-8
# ¡Importante!: 'sql_clause' con ORDER BY sólo es soportado por bases de datos, no por otro tipo de datos
# como dBASE o INFO tables. Para solucionarlo se han copiado los datos a una nueva tabla dentro de una nueva gdb.


import arcpy, os
from datetime import datetime

arcpy.env.overwriteOutput = True

dbf = "Stops_Tabla_seq_0_151.dbf"
flag = False
while not flag:
    # path = input("Ubicacion de " + dbf + ": ")
    path = "C://SyK//03_CURSOR//data"
    arcpy.env.workspace = path
    if arcpy.Exists(dbf):
        flag = True
    else:
        print("Este directorio no contiene el dbf")

stops = os.path.join(path, "Stops.gdb")
if arcpy.Exists(stops):
    arcpy.Delete_management(stops)
arcpy.CreateFileGDB_management(path, "Stops")
arcpy.TableToTable_conversion(dbf, stops, os.path.splitext(dbf)[0])
table = arcpy.env.workspace = os.path.join(path, stops, os.path.splitext(dbf)[0])

arcpy.DeleteField_management(table, "TIEMPO")
arcpy.DeleteField_management(table, "FRECUENCIA")
arcpy.AddField_management(table, "TIEMPO_AUX", "DATE")
arcpy.AddField_management(table, "FRECUENCIA", "FLOAT", field_scale=1)
arcpy.AddField_management(table, "TIEMPO", "TEXT")
arcpy.AddField_management(table, "COD_ITIN", "TEXT")

# Se separan las horas de trip_id y se convierten en tipo de dato fecha
with arcpy.da.UpdateCursor(table, '*') as cursor:
    for row in cursor:
        row[11] = datetime.strptime(row[2][26:34], '%H:%M:%S')
        cursor.updateRow(row)

tiempoList = []
deltaTimeList = []
i = 1
j = 0
# Se crea una lista que almacena las horas para hacer la diferencia entre filas contiguas
with arcpy.da.SearchCursor(table, '*', sql_clause=(None, "ORDER BY trip_id, arrival_ti")) as sCursor:
    for sRow in sCursor:
        tiempoList.append(sRow[11])

# Se calculan las frecuencias mediante una diferencia entre la lista tiempoList[] y el cursor uCursor.
# El resultado se alamacena en la lista deltaTimeList = []. Los datos de esta lista que son de tipo 'deltatime',
# se convierten a dato de tipo flotante, los cuales corresponden a minutos.
with arcpy.da.UpdateCursor(table, '*', sql_clause=(None, "ORDER BY trip_id, arrival_ti")) as uCursor:
    for uRow in uCursor:
        if i < len(tiempoList):
            deltaTimeList.append((tiempoList[i] - uRow[11]).total_seconds() / 60)
            if deltaTimeList[j] > 0:
                uRow[12] = deltaTimeList[j]
            else:
                uRow[12] = None
            uRow[13] = datetime.strftime(uRow[11], '%d/%m/%Y %H:%M:%S')[11:].translate(None, ':')
            uRow[14] = row[2][4:10]
            uCursor.updateRow(uRow)
            i += 1
            j += 1
arcpy.DeleteField_management(table, "TIEMPO_AUX")

# Se localizan los valores unicos de frecuencia
freqList = []
with arcpy.da.SearchCursor(table, '*') as s2Cursor:
    for s2Row in s2Cursor:
        freqList.append(s2Row[11])
uniqFreqList = set(freqList)

arcpy.env.workspace = stops
# Se crean tantas tablas como frecuencias diferentes haya con TableToTable
# Cada una de las tablas solo contendra el valor de frecuencia para cada iteracion del bucle
# Se localizan los valores max y min del campo TIEMPO de cada una de las tablas
for n in uniqFreqList:
    tiempoUniqFrecList = []
    if n is not None:
        nameNewTable = "frec" + str(n)[:len(str(n)) - 2]
        arcpy.MakeTableView_management(table, "tableView", "FRECUENCIA = " + str(n))
        arcpy.TableToTable_conversion("tableView", stops, nameNewTable)
        with arcpy.da.SearchCursor("tableView", '*') as s3Cursor:
            for s3Row in s3Cursor:
                tiempoUniqFrecList.append(s3Row[12])
        # maximo = max(tiempoUniqFrecList)
        # minimo = min(tiempoUniqFrecList)
        # exp = "TIEMPO <> \'" + maximo + "\' AND TIEMPO <> \'" + minimo + "\'"
        # arcpy.MakeTableView_management(nameNewTable, "tableViewDelete", exp)
        # arcpy.DeleteRows_management("tableViewDelete")
