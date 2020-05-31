import arcpy
from datetime import datetime, timedelta

# Funcion que calcula las frecuencias mediante una diferencia entre dos elementos contiguos de la lista tiempoList[]
# El resultado se alamacena en la lista deltaTimeList[]. Los datos de esta lista que son de tipo 'deltatime',
# se convierten a dato de tipo flotante, los cuales corresponden a minutos.
# En caso de que la diferencia sea positiva, el valor se introduce en el campo FRECUENCIA
# En caso de que la diferencia sea negativa significa que el cursor se encuentra en una fila que corresponde al dia
# siguiente, por tanto el valor queda como None
# tiempoList[] contiene las horas y se recorre con el contador i
# deltaTimeList contiene las frecuencias y se recorre con el contador j
def calculateFRECUENCIA (data):
    tiempoList = []
    deltaTimeList = []
    i = 1
    j = 0
    with arcpy.da.SearchCursor(data, '*', sql_clause=(None, "ORDER BY trip_id, arrival_time")) as sCursor:
        for sRow in sCursor:
            tiempoList.append(datetime.strptime(sRow[2], '%H:%M:%S') + timedelta(hours=2))

    with arcpy.da.UpdateCursor(data, '*', sql_clause=(None, "ORDER BY trip_id, arrival_time")) as uCursor:
        for uRow in uCursor:
            if i < len(tiempoList):
                deltaTimeList.append(round((tiempoList[i] - tiempoList[i-1]).total_seconds() / 60))
                if deltaTimeList[j] > 0:
                    uRow[24] = deltaTimeList[j]
                else:
                    uRow[24] = None
                uCursor.updateRow(uRow)
                i += 1
                j += 1


# Funcion que calcula el campo TIEMPO, a partir del campo 'arrival_time'.
# Se convierte a dato de tipo 'date', se suman 2h y posteriormente se vuelve a convertir a tipo 'texto' y
# se eliminan los caracteres innecesarios, como el ':' y la fecha.
def calculateTIEMPO (data):
    with arcpy.da.UpdateCursor(data, '*', sql_clause=(None, "ORDER BY trip_id, arrival_time")) as Cursor:
        for row in Cursor:
            row[25] = (datetime.strptime(row[2], '%H:%M:%S') + timedelta(hours=2)).strftime('%Y/%m/%d %H:%M:%S')[11:].translate(None, ':')
            Cursor.updateRow(row)