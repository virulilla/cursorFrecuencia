import arcpy
from datetime import datetime, timedelta

# Se convierten las horas en tipo de dato fecha
def calculateTimeText(data):
    with arcpy.da.UpdateCursor(data, '*') as cursor:
        for row in cursor:
            row[24] = datetime.strptime(row[2], '%H:%M:%S') + timedelta(hours=2)
            cursor.updateRow(row)


# Funcion que calcula las frecuencias mediante una diferencia entre la lista tiempoList[] y el cursor uCursor.
# El resultado se alamacena en la lista deltaTimeList = []. Los datos de esta lista que son de tipo 'deltatime',
# se convierten a dato de tipo flotante, los cuales corresponden a minutos.
# En caso de que la diferencia sea positiva, el valor se introduce en el campo FRECUENCIA
# En caso de que la diferencia sea negativa significa que el cursor se encuentra en una fila que corresponde al dia
# siguiente, por tanto el valor queda como None
# Se almacena en el campo TIEMPO la hora como tipo de dato Texto
# Se almacena en el campo COD_ITIN el codigo del itinerario
# El contador i recorre tiempoList[]
# El contador j recorre deltaTimeList[]
# tiempoList[] contiene las horas
# deltaTimeList contiene las frecuencias
# Se crea una lista que almacena las horas para hacer la diferencia entre filas contiguas

def calculateFrequency (data):
    tiempoList = []
    deltaTimeList = []
    i = 1
    j = 0
    with arcpy.da.SearchCursor(data, '*', sql_clause=(None, "ORDER BY trip_id, arrival_time")) as sCursor:
        for sRow in sCursor:
            tiempoList.append(sRow[24])

    with arcpy.da.UpdateCursor(data, '*', sql_clause=(None, "ORDER BY trip_id, arrival_time")) as uCursor:
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


