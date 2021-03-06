#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect
import time
from contextlib import suppress
from os import cpu_count
from typing import Any, Type

import torch
import torchsnooper
from draugr import CaptureEarlyStop, MockWriter, add_early_stopping_key_combination, sprint
from draugr.drawers import DiscreteScrollPlot, SeriesScrollPlot
from draugr.torch_utilities import TensorBoardPytorchWriter, torch_seed
from neodroidagent import PROJECT_APP_PATH
from neodroidagent.agents import Agent
from neodroidagent.utilities import NoAgent
from warg import GDKC, passes_kws_to
from warg.context_wrapper import ContextWrapper
from warg.decorators.timing import StopWatch

from .environment_session import EnvironmentSession
from .procedures.procedure_specification import Procedure

__author__ = "Christian Heider Nielsen"
__doc__ = r"""
"""

__all__ = ["SingleAgentEnvironmentSession"]


class SingleAgentEnvironmentSession(EnvironmentSession):
  @passes_kws_to(
      add_early_stopping_key_combination,
      Agent.__init__,
      Agent.save,
      Procedure.__init__,
      Procedure.__call__,
      )
  def __call__(
      self,
      agent: Type[Agent],
      *,
      load_time: Any = str(int(time.time())),
      seed: int = 0,
      save_ending_model: bool = False,
      save_training_resume: bool = False,
      continue_training: bool = True,
      train_agent: bool = True,
      debug: bool = False,
      num_envs: int = cpu_count(),
      **kwargs,
      ):
    """
Start a session, builds Agent and starts/connect environment(s), and runs Procedure


:param args:
:param kwargs:
:return:
"""
    kwargs.update(num_envs=num_envs)
    kwargs.update(train_agent=train_agent)
    kwargs.update(debug=debug)
    kwargs.update(environment=self._environment)

    with ContextWrapper(torchsnooper.snoop, debug):
      with ContextWrapper(torch.autograd.detect_anomaly, debug):

        if agent is None:
          raise NoAgent

        if inspect.isclass(agent):
          sprint(
              "Instantiating Agent", color="crimson", bold=True, italic=True
              )
          torch_seed(seed)
          self._environment.seed(seed)

          agent = agent(load_time=load_time, seed=seed, **kwargs)

        agent_class_name = agent.__class__.__name__

        total_shape = "_".join(
            [
                str(i)
                for i in (
                self._environment.observation_space.shape
                + self._environment.action_space.shape
                + self._environment.signal_space.shape
            )
                ]
            )

        environment_name = f"{self._environment.environment_name}_{total_shape}"

        save_directory = (
            PROJECT_APP_PATH.user_data / environment_name / agent_class_name
        )
        log_directory = (
            PROJECT_APP_PATH.user_log
            / environment_name
            / agent_class_name
            / load_time
        )

        if self._environment.action_space.is_discrete:
          rollout_drawer = GDKC(DiscreteScrollPlot,
                                num_actions=self._environment.action_space.discrete_steps,
                                default_delta=None
                                )
        else:
          rollout_drawer = GDKC(SeriesScrollPlot,
                                window_length=100,
                                default_delta=None
                                )

        if train_agent:  # TODO: allow metric writing while not training with flag
          metric_writer = GDKC(TensorBoardPytorchWriter,
                               path=log_directory
                               )
        else:
          metric_writer = GDKC(MockWriter)

        with ContextWrapper(metric_writer, train_agent) as metric_writer:
          with ContextWrapper(rollout_drawer, num_envs == 1) as rollout_drawer:

            agent.build(
                self._environment.observation_space,
                self._environment.action_space,
                self._environment.signal_space,
                metric_writer=metric_writer,
                )

            kwargs.update(
                environment_name=(self._environment.environment_name,),
                save_directory=save_directory,
                log_directory=log_directory,
                load_time=load_time,
                seed=seed,
                train_agent=train_agent,
                )

            found = False
            if continue_training:
              sprint(
                  "Searching for previously trained models for initialisation for this configuration "
                  "(Architecture, Action Space, Observation Space, ...)",
                  color="crimson",
                  bold=True,
                  italic=True,
                  )
              found = agent.load(
                  save_directory=save_directory, evaluation=not train_agent
                  )
              if not found:
                sprint(
                    "Did not find any previously trained models for this configuration",
                    color="crimson",
                    bold=True,
                    italic=True,
                    )

            if not train_agent:
              agent.eval()
            else:
              agent.train()

            if not found:
              sprint(
                  "Training from new initialisation",
                  color="crimson",
                  bold=True,
                  italic=True,
                  )

            session_proc = self._procedure(agent, **kwargs)

            with CaptureEarlyStop(
                callbacks=self._procedure.stop_procedure, **kwargs
                ):
              with StopWatch() as timer:
                with suppress(KeyboardInterrupt):
                  training_resume = session_proc(
                      metric_writer=metric_writer,
                      rollout_drawer=rollout_drawer,
                      **kwargs
                      )
                  if training_resume and "stats" in training_resume and save_training_resume:
                    training_resume.stats.save(**kwargs)

            end_message = f"Training ended, time elapsed: {timer // 60:.0f}m {timer % 60:.0f}s"
            line_width = 9
            sprint(
                f'\n{"-" * line_width} {end_message} {"-" * line_width}\n',
                color="crimson",
                bold=True,
                italic=True,
                )

            if save_ending_model:
              agent.save(**kwargs)

            try:
              self._environment.close()
            except BrokenPipeError:
              pass

            exit(0)


if __name__ == "__main__":
  print(SingleAgentEnvironmentSession)
