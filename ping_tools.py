#!/usr/bin/env python
#import misc tools
import math


#import tools for dealing with pinging
import os
import requests
import subprocess

#import tools for times
import time
import datetime

import MySQLdb

def ping_host(hostname):
    #print("Pinging host")
    ping_response = subprocess.Popen(["ping", "-c5", hostname],
                                     stdout=subprocess.PIPE).stdout.read()
    #seperate out the response rate and time
    ping_str = ping_response.decode()
    #print(ping_str)
    #print("=============")
    #check if everything has gone wrong
    if 'Ping request could not find host' in ping_str:
        return [0, 0, 0, math.inf, math.inf, math.inf]

    #split it into lines
    rows = ping_str.split('\n')
    times = []

    for ping_result in rows:

        if 'icmp_seq' in ping_result:

            time = ping_result.split('=')[-1]

            time_num = time.split(' ')[0]

            #print(time_num)
            time_num = float(time_num)
            times.append(time_num)

        elif 'transmitted' in ping_result:
           print(ping_result)
           #5 packets transmitted, 3 received, 40% packet loss, time 4064ms
           sent = int(ping_result.split(' ')[0])
           receved = int(ping_result.split(' ')[3])
           lost = sent-receved

           #print('sent')
           #print(sent)
           #print('receved')
           #print(receved)
           #print('lost')
           #print(lost)
           print('BREAKING')
           break


    mx = max(times)
    mn = min(times)
    av = sum(times)/len(times)
    #print('max')
    #print(mx)
    #print('min')
    #print(mn)
    #print('average')
    #print(av)

    return [sent,receved,lost, mn, mx, av]

class ping_capturer(object):

    def __init__(self, user, password, host, database, urls):

        self.db = MySQLdb.connect(host, user, password, database)
        self.urls = urls

    def test_url_and_save_result(self, name, url, database_folder='./output/'):

        event_name = 'pinged_{0}'.format(name)

        [sent, rec, lost, min_spd, max_spd, av_spd] = ping_host(self.urls[name])

        self.curs=self.db.cursor()

        try:
            cmd = "INSERT INTO storedpings values(NOW(), '{0}', {1}, {2}, {3}, {4}, {5}, {6})".format(event_name, sent, rec, lost, min_spd, max_spd, round(av_spd, 2))
            #print(cmd)
            #print("----------")
            self.curs.execute(cmd)

            self.db.commit()
        except Exception as e:
            #print("PROBLEM DETECTED")
            #print(e)
            #print("=================================")
            self.db.rollback()

    def continuous_capture(self):

        while True:

            for name in self.urls.keys():

                self.test_url_and_save_result(name, self.urls[name])
                #wait some time before attempting another collection
            time.sleep(600)
            print("RECOLLECTING")

###################################
### End of function definitions ###
###################################

#the urls we are going to use to test the connection
#urls = {'google':'google.co.uk', 'google_DNS_server':'8.8.8.8',
#        'Virgin_media':'virginmedia.com'}#,'bad':'jdfalsdhbfafdib.liasdbfaib.co'}

#storer = ping_capturer('down', 'virgin', 'localhost', 'pingstore')

#storer.continuous_capture(urls)



