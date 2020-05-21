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

# arcpy.Sort_management(dbf, "dbf_sorted", [["trip_id", "ASCENDING"], ["arrival_ti", "ASCENDING"]])

# listField = ["OID", "OBJECTID", "trip_id", "arrival_ti", "departure", "stop_id", "stop_seque", "stop_heads", "pickup_typ", "drop_off_t", "shape_dist", "TIEMPO", "FRECUENCIA"]

tiempoList = []
i = 1
with arcpy.da.SearchCursor(dbf, '*', sql_clause=(None, "ORDER BY trip_id, arrival_ti")) as sCursor:
    for sRow in sCursor:
        tiempoList.append(sRow[11])

with arcpy.da.UpdateCursor(dbf, '*', sql_clause=(None, "ORDER BY trip_id, arrival_ti")) as uCursor:
    for uRow in uCursor:
        if i < len(tiempoList):
            # uRow.next()
            uRow[12] = tiempoList[i] - uRow[11]
            uCursor.updateRow(uRow)
            i += 1

