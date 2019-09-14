#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import types
from typing import Type

import torch

from draugr.visualisation import sprint
from neodroidagent.agents.agent import Agent
from neodroidagent.agents.random_agent import RandomAgent
from neodroidagent.exceptions.exceptions import NoProcedure
from neodroidagent.procedures import RolloutInference, Procedure, Episodic
from neodroidagent.sessions import ParallelSession
from neodroidagent.sessions.linear import LinearSession
from neodroidagent.sessions.parse_arguments import parse_arguments
from neodroidagent.utilities.specifications import EnvironmentSession
from warg.arguments import config_to_mapping
from warg.named_ordered_dictionary import NOD

__author__ = 'Christian Heider Nielsen'
__doc__ = ''


def session_entry_point(agent: Type[Agent],
                        config: object,
                        *,
                        session: EnvironmentSession = LinearSession,
                        parse_args: bool = True,
                        save: bool = True,
                        has_x_server: bool = True,
                        skip_confirmation: bool = True
                        ):
  r'''
    Entry point start a starting a training session with the functionality of parsing cmdline arguments and
    confirming configuration to use before training and overwriting of default training configurations
  '''

  if parse_args:
    args = parse_arguments(f'{type(agent)}', NOD(config.__dict__))

    skip_confirmation = args.SKIP_CONFIRMATION

    if args.INFERENCE:
      if args.PRETRAINED_PATH != '':
        session._procedure = RolloutInference

    # TODO: load earlier model and inference flags

    if 'CONFIG' in args.keys() and args['CONFIG']:
      import importlib.util
      spec = importlib.util.spec_from_file_location('overloaded.config', args['CONFIG'])
      config = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(config)
    else:
      for key, arg in args.items():
        if key != 'CONFIG':
          setattr(config, key, arg)

  if has_x_server:
    display_env = os.getenv('DISPLAY', None)
    if display_env is None:
      config.RENDER_ENVIRONMENT = False
      has_x_server = False

  config_mapping = config_to_mapping(config)

  if not skip_confirmation:
    sprint(f'\nUsing config: {config}\n',
           highlight=True,
           color='yellow')
    for key, arg in config_mapping:
      print(f'{key} = {arg}')

    sprint(f'\n.. Also save:{save},'
           f' has_x_server:{has_x_server}')
    input('\nPress Enter to begin... ')

  if session is None:
    raise NoProcedure
  elif isinstance(session, (types.ClassType)):
    session = session(config_mapping.environment_name, **config_mapping)

  try:
    session(agent,
            save=save,
            has_x_server=has_x_server,
            **config_mapping)
  except KeyboardInterrupt:
    print('Stopping')

  torch.cuda.empty_cache()

  exit(0)


if __name__ == '__main__':
  import neodroidagent.configs.base_config as C

  session_entry_point(RandomAgent,
                      C,
                      session=ParallelSession(
                        'connect_to_running',
                        RolloutInference,
                        connect_to_running=True,
                        auto_reset_on_terminal_state=True))