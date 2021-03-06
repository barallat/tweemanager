# -*- coding:utf-8 -*-
import pymongo
import datetime
import json

# IP host should be changed to your MongoDB server
client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
db = client.tweets
coll = db.tweem_default # Coll should be changed to the collection that you to report
name_collection = coll.name

# 1º ListOfdays:
def genListOfdays(StartDate, EndDate=datetime.datetime.now()):
    """
    """
    onedaydelta = datetime.timedelta(days=1)
    StartDate = datetime.datetime(StartDate.year, StartDate.month, StartDate.day)
    EndDate = datetime.datetime(EndDate.year, EndDate.month, EndDate.day)
    delta = EndDate - StartDate
    for i in xrange(delta.days):
        yield {'start': StartDate, 'end': StartDate + onedaydelta}
        StartDate += onedaydelta


# 2º ListOfWeeks:
def genListOfWeeks(StartDate, EndDate):
    """
    """
    onedaydelta = datetime.timedelta(days=1)
    oneweekdelta = datetime.timedelta(days=7)
    StartDate = datetime.datetime(StartDate.year, StartDate.month, StartDate.day)
    while StartDate.weekday() != 0:
        StartDate = StartDate - onedaydelta
    EndDate = datetime.datetime(EndDate.year, EndDate.month, EndDate.day) + onedaydelta
    deltadays = EndDate - StartDate
    deltaweeks = deltadays.days / 7
    for i in xrange(deltaweeks + 1):
        yield {'start': StartDate, 'end': StartDate + oneweekdelta}
        StartDate += oneweekdelta

# 3º ListOfMonth:
def genListOfMonth(StartDate,EndDateInp):
    """
    """
    StartDate = datetime.datetime(StartDate.year, StartDate.month, 1)
    EndDate = datetime.datetime(StartDate.year, StartDate.month, 1)

    def addMonth(Date):
        """
        """
        #year = Date.year + (Date.month + 2) / 12
        year = Date.year + (Date.month / 12)
        month  = ((Date.month) % 12) + 1
        monthplusone = datetime.datetime(year , month  , Date.day)
        return monthplusone

    while EndDate < EndDateInp:
        EndDate = addMonth(StartDate)
        yield {'start': StartDate, 'end': EndDate}
        StartDate = EndDate


# Agg Functions:
def aggCount(StartDate, EndDate):
    """
    It returns the number of tweets between a time interval
    """
    # Classifier and values should be change to use your owns
    pipeline = [
        {"$match": {"$and": [{"created_at": {"$gte": StartDate}}, {"created_at": {"$lt": EndDate}}]}},
        {"$group": {"_id": "",
        "count": {"$sum": 1},
        "npos": {"$sum": {"$cond":[{"$eq":["$valoration.classifier1.value","positive"]},1,0]}},
        "nneg": {"$sum": {"$cond":[{"$eq":["$valoration.classifier1.value","negative"]},1,0]}},
        "met": {"$sum": "$valoration.classifier1.metric"}
        }},
    ]

    result = {'count':0, 'npos':0, 'nneg':0, 'met':0}
    for result in coll.aggregate(pipeline):
        result = result
    return result


# Reports to a JSON file
def report_to_JSON(StartDate, EndDate):
    outfile = open('report_days.json', 'w')
    # 1º ListOfDays:
    print("Writing report by days...")
    for values in genListOfdays(StartDate, EndDate):
        linea = {}
        valor = aggCount(values['start'], values['end'])
        linea['tweets'] = valor['count']
        linea['positives'] = valor['npos']
        linea['negatives'] = valor['nneg']
        linea['metrica'] = valor['met']
        linea = json.dumps(linea)
        outfile.write(linea)
        outfile.write("\n")
    outfile.close()

    outfile = open('report_weeks.json', 'w')
    # 2º ListOfWeeks:
    print("Writing report by weeks...")
    for values in genListOfWeeks(StartDate, EndDate):
        linea = {}
        valor = aggCount(values['start'], values['end'])
        linea['tweets'] = valor['count']
        linea['positives'] = valor['npos']
        linea['negatives'] = valor['nneg']
        linea['metrica'] = valor['met']
        linea = json.dumps(linea)
        outfile.write(linea)
        outfile.write("\n")
    outfile.close()

    outfile = open('report_months.json', 'w')
    # 3º ListOfMonth:
    print("Writing report by monts...")
    for values in genListOfMonth(StartDate, EndDate):
        linea = {}
        valor = aggCount(values['start'], values['end'])
        linea['tweets'] = valor['count']
        linea['positives'] = valor['npos']
        linea['negatives'] = valor['nneg']
        linea['metrica'] = valor['met']
        linea = json.dumps(linea)
        outfile.write(linea)
        outfile.write("\n")
    outfile.close()

# Reports to MongoDB
def report_to_Mongo(StartDate, EndDate, name_collection):
    coll = db.Reporting
    
    # 1º ListOfDays:
    print("Uploading report by days...")
    for values in genListOfdays(StartDate, EndDate):
        linea = {}
        valor = aggCount(values['start'], values['end'])
        linea['date'] = values['start']
        linea['start'] = values['start']
        linea['end'] = values['end']
        linea['tweets'] = valor['count']
        linea['positives'] = valor['npos']
        linea['negatives'] = valor['nneg']
        linea['metrica'] = valor['met']
        linea['report'] = {'type':'daily', 'from':name_collection}
        key = values['start'].strftime("%Y%m%d") + values['end'].strftime("%Y%m%d")
        coll.update({"_id":key}, linea, upsert = True)

    # 2º ListOfWeeks:
    print("Uploading report by weeks...")
    for values in genListOfWeeks(StartDate, EndDate):
        linea = {}
        valor = aggCount(values['start'], values['end'])
        linea['date'] = values['start']
        linea['start'] = values['start']
        linea['end'] = values['end']
        linea['tweets'] = valor['count']
        linea['positives'] = valor['npos']
        linea['negatives'] = valor['nneg']
        linea['metrica'] = valor['met']
        linea['report'] = {'type':'weekly', 'from':name_collection}
        key = values['start'].strftime("%Y%m%d") + values['end'].strftime("%Y%m%d")
        coll.update({"_id":key}, linea, upsert = True)

    # 3º ListOfMonth:
    print("Uploading report by monts...")
    for values in genListOfMonth(StartDate, EndDate):
        linea = {}
        valor = aggCount(values['start'], values['end'])
        linea['date'] = values['start']
        linea['start'] = values['start']
        linea['end'] = values['end']
        linea['tweets'] = valor['count']
        linea['positives'] = valor['npos']
        linea['negatives'] = valor['nneg']
        linea['metrica'] = valor['met']
        linea['report'] = {'type':'monthly', 'from':name_collection}
        key = values['start'].strftime("%Y%m%d") + values['end'].strftime("%Y%m%d")
        coll.update({"_id":key}, linea, upsert = True)


if __name__ == '__main__':

    # 1º get first date
    for tweet in coll.find().sort('created_at', 1).limit(1):
        StartDate = tweet['created_at']
    print(StartDate)

    # 2º get last date
    for tweet in coll.find().sort('created_at', -1).limit(1):
        EndDate = tweet['created_at']
    print(EndDate)

    # 3º get all data:
    # Uploading to MongoDB
    report_to_Mongo(StartDate, EndDate, name_collection)

    # Write the reporting in a JSON file
    report_to_JSON(StartDate, EndDate)

    # Perform aggregations on the time table:
    # 1º ListOfdays:
    print("Por días")
    for values in genListOfdays(StartDate, EndDate):
        valor = aggCount(values['start'], values['end'])
        print("Tweets")
        print(values['start'].strftime("%Y-%m-%d"),
            values['end'].strftime("%Y-%m-%d"))
        print(valor)
        print("")

    # 2º ListOfWeeks:
    print("Por semanas")
    for values in genListOfWeeks(StartDate, EndDate):
        valor = aggCount(values['start'], values['end'])
        print("Tweets")
        print(values['start'].strftime("%Y-%m-%d"),
              values['end'].strftime("%Y-%m-%d"))
        print(valor)
        print("")

    # 3º ListOfMonth:
    print("Por meses")
    for values in genListOfMonth(StartDate, EndDate):
        valor = aggCount(values['start'], values['end'])
        print("Tweets")
        print(values['start'].strftime("%Y-%m-%d"),
              values['end'].strftime("%Y-%m-%d"))
        print(valor)
        print("")