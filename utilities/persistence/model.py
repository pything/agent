#!/usr/bin/env python3
# coding=utf-8
__author__ = 'cnheider'
import datetime
import glob
import os
import shutil
import sys

import torch


def load_model(configuration, latest=True):
  _list_of_files = glob.glob(configuration.MODEL_DIRECTORY + '/*')
  _latest_model = max(_list_of_files, key=os.path.getctime)
  print('loading previous model: ' + _latest_model)

  return torch.load(_latest_model)


def save_model(model, configuration, name=''):
  _model_date = datetime.datetime.now()
  prepend = ''
  if len(name) > 0:
    prepend = f'{name}-'
  _model_name = prepend + \
                f'{configuration.PROJECT}-' \
                f'{configuration.CONFIG_NAME.replace('.','_')}-' \
                f'{_model_date.strftime('%y%m%d%H%M')}.model'

  _model_path = os.path.join(configuration.MODEL_DIRECTORY, _model_name)
  torch.save(
      model.state_dict(), _model_path
      )  # TODO possible to .cpu() copy would be great
  save_config(_model_path, configuration)
  print('Saved model at {}'.format(_model_path))


def save_config(model_path, configuration):
  config_path = os.path.join(
      configuration.CONFIG_DIRECTORY, configuration.CONFIG_FILE
      )
  shutil.copyfile(config_path, model_path + '.py')


def convert_to_cpu(path=''):
  model = torch.load(path, map_location=lambda storage, loc: storage)
  torch.save(model, path + '.cpu')


if __name__ == '__main__':
  convert_to_cpu(sys.argv[1])
