import json
import time
from datetime import datetime
from flask import Flask, request, render_template, Response, redirect
import MySQLdb
import datetime

import threading
import ping_tools as pt
import logging

logger = logging.getLogger("down_detector_logs")

hdlr = logging.FileHandler("./logging/down_detection_logs.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


logger.info("STARTING COLLECTION")
ping_urls = {'google':'google.co.uk', 'google_DNS_server':'8.8.8.8',
        'Virgin_media':'virginmedia.com'}

#start collecting PING data in a seperate thread
storer = pt.ping_capturer('down', 'virgin', 'localhost', 'pingstore', ping_urls)

thread = threading.Thread(target=storer.continuous_capture)
thread.daemon = True
thread.start()

#storer.continuous_capture()

app = Flask(__name__)
 
@app.route("/")
def index():
    return redirect("/lines/recent")

@app.route("/download_all_data")
def data_dump():

    logger.info("ALL DATA WAS REQUESTED BY {0}".format(request.remote_addr))

    grab_cmd = "SELECT * from storedpings"
    
    db = MySQLdb.connect("localhost", "down", "virgin", "pingstore")
    curs = db.cursor()

    curs.execute(grab_cmd)

    out_string = "Time,Event,SentPings,RecevedPings,LostPings"
    out_string += ",MinPingTime,MaxPingTime,MeanPingTime"

    #fetch data from the sql server and dump it into a csv
    for rowi, row in enumerate(curs.fetchall()):
        
        out_string += '\n' + str(row[0])
        for i in range(len(row)-1):
            out_string += ',' + str(row[i+1])

    return Response(out_string,
                    mimetype="text/csv",
                    headers={"Content-disposition":
                             "attachment; filename=all_pinging_data_{0}.csv".format(time.strftime("%Y_%m_%d-%H_%M_%S"))})

@app.route("/lines/<period>")
def line_shower(period):

    print("GOT A REQUEST")
    print(request.remote_addr)
    print("=======================")

    logger.info("{0} graph was requested by {1}".format(period, request.remote_addr))

    #set up for the period we're interested in
    if period == 'day':
        #print("FOUND DAY")
        sql_period = '1 DAY'
        plot_period = 'hour'

    elif period == 'month':
        #print("FOUND MONTH")
        sql_period = '1 MONTH'
        plot_period = 'day'

    elif period == 'year':
        #print("FOUND YEAR")
        sql_period = '1 YEAR'
        plot_period = 'month'

    else:
        print("INVALID PERIOD, REVERTING TO DEFAULT")
        sql_period = '2 HOUR'
        plot_period = 'minute'


    grab_cmd = "SELECT * from storedpings WHERE time >= now()- INTERVAL {0};".format(sql_period)
    
    #print(grab_cmd)
    #print("========================")
    #grab the data from SQL, reconnect each time to get the latest data
    db = MySQLdb.connect("localhost", "down", "virgin", "pingstore")
    curs = db.cursor()

    curs.execute(grab_cmd)

    dataJSON = [{'label':'Google pings',
                'borderColor': "rgba(0,0,220,1)",
                'backgroundColor': "rgba(0,0,220,0.2)",
                'pointBorderColor': "rgba(0,0,220,1)",
                'pointBackgroundColor': "rgba(0,0,220,1)",
                'bezierCurve' : 'false',
                'lineTension': 0,
                'data':[]},
                {'label':'Google DNS pings',
                'borderColor': "rgba(220,0,0,1)",
                'backgroundColor': "rgba(220,0,0,0.2)",
                'pointBorderColor': "rgba(220,0,0,1)",
                'pointBackgroundColor': "rgba(220,0,0,1)",
                'bezierCurve' : 'false',
                'lineTension': 0,
                'data':[]},{'label':'Virgin media pings',
                'borderColor': "rgba(0,220,0,1)",
                'backgroundColor': "rgba(0,220,0,0.2)",
                'pointBorderColor': "rgba(0,220,0,1)",
                'pointBackgroundColor': "rgba(0,220,0,1)",
                'bezierCurve' : 'false',
                'lineTension': 0,
                'data':[]}]

    #run through the grabbed data and plot it on a graph
    for rowi, row in enumerate(curs.fetchall()):

        if row[1] == 'pinged_google':
            x = row[0].strftime("%Y-%m-%d %H:%M:%S")
            y = row[3]

            dataJSON[0]['data'].append({'x':x, 'y':y})

        elif row[1] == 'pinged_google_DNS_server':
            x = row[0].strftime("%Y-%m-%d %H:%M:%S")
            y = row[3]

            dataJSON[1]['data'].append({'x':x, 'y':y})

        elif row[1] == 'pinged_Virgin_media':
            x = row[0].strftime("%Y-%m-%d %H:%M:%S")
            y = row[3]

            dataJSON[2]['data'].append({'x':x, 'y':y})

        else:
            print(row[1])
            print("********************")

    #close the connections to avoid memory leaks
    curs.close()
    db.close()


    #reduce the number of datapoints to make sure I don't crash the server
    max_datapoints = 100
    for datai, dataset in enumerate(dataJSON):
        if len(dataset['data']) > max_datapoints:
            factor = len(dataset['data'])//max_datapoints
            out_list = []

            for i, point in enumerate(dataset['data']):
            
                if i % factor == 0:
                
                    out_list.append(point)
            
            dataJSON[datai]['data'] = out_list


    #render the template
    return render_template('show_time_lines.html',
                           example_text='Holy hell it\'s here',
                           dataset = dataJSON,
                           time_units=plot_period,
                           day_link='/lines/day',
                           month_link='/lines/month',
                           year_link='/lines/year',
                           download_link='/download_all_data')


#estabish the connection to the database
#db = MySQLdb.connect("localhost", "down", "virgin", "pingstore")
logger.info("STARTING FLASK SERVER")

if __name__ == "__main__":
    app.run(host= '0.0.0.0', debug=True)

