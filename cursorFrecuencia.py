# ¡Importante!: 'sql_clause' con ORDER BY sólo es soportado por bases de datos, no por otro tipo de datos
# como dBASE o INFO tables. Para solucionarlo se han copiado los datos a una nueva tabla dentro de una nueva gdb.


import arcpy, os
arcpy.env.overwriteOutput = True

dbf = "Stops_Tabla_seq_0_151.dbf"
flag = False
while not flag:
    path = input("Ubicacion de " + dbf + ": ")
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

tiempoList = []
i = 1
with arcpy.da.SearchCursor(table, '*', sql_clause=(None, "ORDER BY trip_id, arrival_ti")) as sCursor:
    for sRow in sCursor:
        tiempoList.append(sRow[11])

with arcpy.da.UpdateCursor(table, '*', sql_clause=(None, "ORDER BY trip_id, arrival_ti")) as uCursor:
    for uRow in uCursor:
        if i < len(tiempoList):
            uRow[12] = tiempoList[i] - uRow[11]
            uCursor.updateRow(uRow)
            i += 1

