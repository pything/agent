#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from agent.architectures import MLP
from .base_test_config import *

__author__ = 'cnheider'
'''
Description: Config for training
Author: Christian Heider Nielsen
'''

CONFIG_NAME = __name__
CONFIG_FILE = __file__

# Exploration
EXPLORATION_EPSILON_START = 1.0
EXPLORATION_EPSILON_END = 0.04
EXPLORATION_EPSILON_DECAY = 400

INITIAL_OBSERVATION_PERIOD = 0
LEARNING_FREQUENCY = 1
REPLAY_MEMORY_SIZE = 10000
MEMORY = U.ReplayBuffer(REPLAY_MEMORY_SIZE)

BATCH_SIZE = 128
DISCOUNT_FACTOR = 0.999
RENDER_ENVIRONMENT = True
SIGNAL_CLIPPING = True
DOUBLE_DQN = True
SYNC_TARGET_MODEL_FREQUENCY = 1000

# EVALUATION_FUNCTION = lambda Q_state, Q_true_state: (Q_state - Q_true_state).pow(2).mean()

VALUE_ARCH = MLP
OPTIMISER_TYPE = torch.optim.RMSprop  # torch.optim.Adam

# Architecture
VALUE_ARCH_PARAMETERS = NOD(**{
  'input_size':             None,  # Obtain from environment
  'hidden_layers':          None,
  'output_size':            None,  # Obtain from environment
  'hidden_layer_activation':torch.relu,
  'use_bias':               True,
  })