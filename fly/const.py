from enum import Enum


class EngineState(Enum):
    ENGINE_STATE_RUNNING = 1
    ENGINE_STATE_STOPPING = 2
    ENGINE_STATE_STOPPED = 3
