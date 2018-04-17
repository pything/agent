#!/usr/bin/env python3
# coding=utf-8
__author__ = 'cnheider'

from configs.base_config import *

CONFIG_NAME = __name__
CONFIG_FILE = __file__

ENVIRONMENT_NAME = 'grid_world'
# CONNECT_TO_RUNNING = True
RENDER_ENVIRONMENT = True

EVALUATION_FUNCTION = torch.nn.CrossEntropyLoss

# Architecture
POLICY_ARCH_PARAMS = {
  'input_size':    '',  # Obtain from environment
  'activation':    F.leaky_relu,
  'hidden_layers': [128, 64, 32, 16],
  'output_size':   '',  # Obtain from environment
  'use_bias':      False
  }
POLICY_ARCH = CategoricalMLP
