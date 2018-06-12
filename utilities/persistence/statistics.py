#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'cnheider'

import csv
import datetime
import os


def save_statistic(statistic, name, LOG_DIRECTORY='logs', PROJECT='', CONFIG_NAME='', **kwargs):
  _file_date = datetime.datetime.now()
  _file_name = f'{PROJECT}-{CONFIG_NAME.replace(".", "_")}-{_file_date.strftime("%y%m%d%H%M")}.{name}.csv'
  _file_path = os.path.join(LOG_DIRECTORY, _file_name)

  stat = [[s] for s in statistic]
  with open(_file_path, 'w') as f:
    w = csv.writer(f)
    w.writerows(stat)
  print('Saved statistics_utilities at {}'.format(_file_path))
