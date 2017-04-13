#!/usr/bin/env python

from __future__ import print_function
import sys
if sys.version_info.major != 3:
    print ("need python 3 for this script")
    sys.exit(1)

from datetime import datetime
import re, time, argparse

from argparse import ArgumentParser
ap = ArgumentParser()
ap.add_argument('--threshold', metavar='RATE', type=float, default=0.,
                dest='threshold',
                help='Rate (in Mbit/s) below which output is supressed')
ap.add_argument('--interval', metavar='INTERVAL', type=float, default=1000.,
                dest='interval',
                help='Sampling interval (in milliseconds)')

args = ap.parse_args()

threshold = (args.threshold * 1024 * 1024 / 8)
interval = args.interval / 1000.
line_re = re.compile(r'\s*(.*):\s*(\d+)(?:\s+\d+){7}\s+(\d+)(?:\s+\d+){7}\s*')

then = None
old_stat = {}
while True:
    now = datetime.utcnow()
    new_stat = {}
    for line in open('/proc/net/dev').readlines()[2:]:
        m = line_re.match(line)
        dev, rx, tx = m.groups()
        new_stat[dev] = (int(rx), int(tx))
    rates = {}
    for key in old_stat.keys() & new_stat.keys():
        new = new_stat[key]
        old = old_stat[key]
        def rate(n):
            return int((new[n] - old[n]) / (now - then).total_seconds())
        rates[key] = (rate(0), rate(1))
    if any([rate[0] >= threshold or rate[1] >= threshold
            for rate in rates.values()]):
        print('{} UTC'.format(now), end='')
        for key in sorted(rates.keys()):
#          if key.startswith('eth'):
          rx, tx = rates[key]
          if rx >= threshold or tx >= threshold:
            print(' || \x1b[0;30;41m {:4} {:4}m(rx) {:4}m(tx) \x1b[0m '.format(key, round(rx/1024/1024*8), round(tx/1024/1024*8)), end='')
          else:
            print(' || \x1b[6;30;42m {:4} {:4}m(rx) {:4}m(tx) \x1b[0m '.format(key, round(rx/1024/1024*8), round(tx/1024/1024*8)), end='')
        print('')
    old_stat = new_stat
    then = now
    time.sleep(interval)
