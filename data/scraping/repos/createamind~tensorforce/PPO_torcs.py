# Copyright 2017 reinforce.io. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================




from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import logging
import os

from tensorforce import Configuration, TensorForceError
from tensorforce.core.networks import from_json

from tensorforce.agents import agents, TRPOAgent
from tensorforce.agents.ppo_agent_noise import PPOAgent
#from tensorforce.environments.openai_gym import OpenAIGym
from tensorforce.execution import Runner
from tensorforce.core.networks import layered_network_builder
from gym_torcs import GymTorcsEnv

import numpy as np


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-gym_id', help="ID of the gym environment")
    parser.add_argument('-a', '--agent', help='Agent')
    parser.add_argument('-c', '--agent-config', help="Agent configuration file")
    parser.add_argument('-n', '--network-config', help="Network configuration file")
    parser.add_argument('-e', '--episodes', type=int, default=50000, help="Number of episodes")
    parser.add_argument('-t', '--max-timesteps', type=int, default=50000, help="Maximum number of timesteps per episode")
    parser.add_argument('-m', '--monitor', help="Save results to this directory")
    parser.add_argument('-ms', '--monitor-safe', action='store_true', default=False, help="Do not overwrite previous results")
    parser.add_argument('-mv', '--monitor-video', type=int, default=0, help="Save video every x steps (0 = disabled)")
    parser.add_argument('-s', '--save', help="Save agent to this dir")
    parser.add_argument('-se', '--save-episodes', type=int, default=100, help="Save agent every x episodes")
    parser.add_argument('-l', '--load', help="Load agent from this dir")
    parser.add_argument('-D', '--debug', action='store_true', default=True, help="Show debug outputs")
    parser.add_argument('-p', '--port', type=int, default=3202, help="Show debug outputs")
    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # configurable!!!

    #environment = OpenAIGym(args.gym_id, monitor=args.monitor, monitor_safe=args.monitor_safe, monitor_video=args.monitor_video)
    env = GymTorcsEnv(port=args.port)

    if args.agent_config:
        agent_config = Configuration.from_json(args.agent_config)
    else:
        agent_config = Configuration.from_json('configs/ppo_cartpole.json' )
        #agent_config = Configuration()
        #logger.info("No agent configuration provided.")
    if args.network_config:
        network = from_json(args.network_config)
    else:
        network = from_json('configs/ppo_network.json')
        #network = None
        #logger.info("No network configuration provided.")
    agent_config.default(dict(states=env.states, actions=env.actions, network=network))
    #agent_config.default(dict(states=environment.states, actions=environment.actions, network=network))
    #agent = agents[args.agent](config=agent_config)
    agent = PPOAgent(config=agent_config)

    #args.load = './model/'
    if args.load:
        load_dir = os.path.dirname(args.load)
        if not os.path.isdir(load_dir):
            raise OSError("Could not load agent from {}: No such directory.".format(load_dir))
        agent.load_model(args.load)
        logger.info("------------------------------------------------------model loaded !! --------------------------------")

    if args.debug:
        logger.info("-" * 16)
        logger.info("Configuration:")
        logger.info(agent_config)

    #args.save = './model/'
    if args.save:
        save_dir = os.path.dirname(args.save)
        if not os.path.isdir(save_dir):
            try:
                os.mkdir(save_dir, 0o755)
            except OSError:
                raise OSError("Cannot save agent to dir {} ()".format(save_dir))

    runner = Runner(
        agent=agent,
        environment=env,
        repeat_actions=1,
        save_path=args.save,
        save_episodes=args.save_episodes,
        #render=True,

    )

    report_episodes = 1 #args.episodes // 1000
    if args.debug:
        report_episodes = 1

    def episode_finished(r):
        if r.episode % report_episodes == 0:
            logger.info("Finished episode {ep} after {ts} timesteps".format(ep=r.episode, ts=r.timestep))
            logger.info("Episode reward: {}".format(r.episode_rewards[-1]))
            logger.info("Average of last 500 rewards: {}".format(sum(r.episode_rewards[-500:]) / 500))
            logger.info("Average of last 100 rewards: {}".format(sum(r.episode_rewards[-100:]) / 100))
        if np.mod(r.episode, 59) == 0:
            env.reset(relaunch=True)
        return True

    logger.info("Starting {agent} for Environment '{env}'".format(agent=agent, env=env))
    runner.run(args.episodes, args.max_timesteps, episode_finished=episode_finished)
    logger.info("Learning finished. Total episodes: {ep}".format(ep=runner.episode))

    # if args.monitor:
    #     environment.gym.monitor.close()
    # environment.close()


if __name__ == '__main__':
    main()
