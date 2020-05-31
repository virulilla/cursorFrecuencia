import arcpy

class uniqRouteIdClass:
    def __init__(self, vRow):
        # self.OBJECTID = vRow[0]
        # self.trip_id = ''
        # self.arrival_time = ''
        # self.departure_time = ''
        # self.stop_id = ''
        # self.stop_sequence = 0
        # self.OBJECTID_1 = 0
        self.route_id = vRow[7]
        # self.route_id_X = 0
        # self.route_id_Y = 0
        # self.service_id = ''
        # self.trip_id_1 = ''
        # self.shape_id = ''
        # self.OBJECTID_12 = 0
        # self.service_id_1 = ''
        self.monday = vRow[15]
        self.tuesday = vRow[16]
        self.wednesday = vRow[17]
        self.thursday = vRow[18]
        self.friday = vRow[19]
        self.saturday = vRow[20]
        self.sunday = vRow[21]
        # self.start_date = 0
        # self.end_date = 0
        self.FRECUENCIA = vRow[24]
        self.TIEMPO = vRow[25]

def rellenaUniqRouteIdClass(data):
    dayViewList = []
    with arcpy.da.SearchCursor(data, '*') as moduleCursor:
        for dataRow in moduleCursor:
            dayViewList.append(uniqRouteIdClass(dataRow))
    return dayViewList