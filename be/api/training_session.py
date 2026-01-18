import threading
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agent import DQNAgent
from SubGraph import Y_RANGE
from api.constants import MODEL_SAVE_INTERVAL, TRAINING_BATCH_SIZE, TRAINING_BUFFER_SIZE


def compute_state_dim():
    """Compute state dimension based on SubGraph parameters."""
    return (Y_RANGE ** 2) * 6 + 100 * 2 + 4 * 2


class TrainingSession:
    """Thread-safe manager for a single DQN training session."""

    def __init__(self, world, session_id, num_workers, eval_mode=False):
        self.world = world
        self.session_id = session_id
        self.num_workers = num_workers
        self.eval_mode = eval_mode
        self.is_running = False
        self.is_paused = False
        self.lock = threading.Lock()
        self.total_reward = 0
        self.step_count = 0
        self.episode = 0

        model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'model_eval.pth'
        )

        state_dim = compute_state_dim()
        self.agent = DQNAgent(
            state_dim=state_dim,
            action_dim=4,
            model_path=model_path,
            save_interval=MODEL_SAVE_INTERVAL,
            batch_size=TRAINING_BATCH_SIZE,
            buffer_size=TRAINING_BUFFER_SIZE
        )

        if eval_mode:
            self.agent.epsilon = 0.0

        for worker in self.world.workers:
            worker.setup_worker()

    def step(self):
        """Execute one training step for all workers. Returns True if simulation should continue."""
        if not self.is_running or self.is_paused:
            return False

        with self.lock:
            if self.world.is_finished():
                return False

            step_reward = 0
            for worker in self.world.workers:
                action = self.agent.act(worker.state)
                next_state, reward, done = worker.play(action)

                if not self.eval_mode:
                    self.agent.remember(worker.state, action, reward, next_state, done)
                    self.agent.train()

                worker.state = worker.get_state()
                step_reward += reward

            self.total_reward += step_reward
            self.step_count += 1

            return not self.world.is_finished()

    def start(self):
        with self.lock:
            self.is_running = True
            self.is_paused = False

    def stop(self):
        with self.lock:
            self.is_running = False

    def pause(self):
        with self.lock:
            self.is_paused = True

    def resume(self):
        with self.lock:
            self.is_paused = False

    def get_state_update(self):
        """Get current state for streaming to frontend."""
        graph = self.world.graph
        graph_dict = graph.to_dict()
        workers_list = graph.get_workers_dict(self.world.workers)
        progress = graph.clean_ratio()

        return {
            'edges': graph_dict['edges'],
            'workers': workers_list,
            'progress': progress,
            'training': self.get_training_metrics()
        }

    def get_initial_state(self):
        """Get full initial state including nodes."""
        graph = self.world.graph
        graph_dict = graph.to_dict()
        workers_list = graph.get_workers_dict(self.world.workers)
        progress = graph.clean_ratio()

        return {
            **graph_dict,
            'workers': workers_list,
            'progress': progress,
            'training': self.get_training_metrics()
        }

    def get_training_metrics(self):
        """Get current training metrics."""
        agent_metrics = self.agent.get_metrics()
        return {
            'episode': self.episode,
            'total_reward': self.total_reward,
            'step_count': self.step_count,
            'eval_mode': self.eval_mode,
            **agent_metrics
        }
