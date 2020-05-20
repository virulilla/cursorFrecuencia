import arcpy, os
arcpy.env.overwriteOutput = True


dbf = "Stops_Tabla_seq_0_151.dbf"
flag = False
while not flag:
    path = input("Ubicación de " + dbf + ": ")
    arcpy.env.workspace = path
    if arcpy.Exists(dbf):
        flag = True
        arcpy.env.workspace = os.path.join(path, dbf)
    else:
        print("Este directorio no contiene el dbf")

arcpy.Sort_management(dbf, "dbf_sorted", [["trip_id", "ASCENDING"], ["arrival_ti", "ASCENDING"]])
