#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC
from itertools import count
from typing import Any

from tqdm import tqdm

from agents.abstract.agent import Agent

__author__ = 'cnheider'
from agents.abstract.torch_agent import TorchAgent


class EVOAgent(Agent, ABC):
  '''
  Base class for evolution strategy (ES) based agents
  '''

  # region Public

  def sample_action(self, state, **kwargs):
    pass

  def evaluate(self, batch, **kwargs):
    pass

  def rollout(self, initial_state, environment, *, train=True, render=False, **kwargs) -> Any:
    if train:
      self._rollout_i += 1

    episode_signal = 0
    episode_length = 0

    state = initial_state

    T = count(1)
    T = tqdm(T, f'Rollout #{self._rollout_i}', leave=False)

    for t in T:
      action = int(self.sample_action(state)[0])


      (state, signal, terminated, info) = environment.step(action=action)
      episode_signal += signal

      if render:
        environment.render()

      if terminated:
        episode_length = t
        break

    if train:
      self.update()

    return episode_signal, episode_length

  # endregion

  # region Protected

  def _optimise_wrt(self, error, **kwargs):
    pass

  # endregion