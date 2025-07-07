import numpy as np

from multiprocessing import shared_memory
from typing import Dict


class SharedImageList:
    def __init__(self, camera_config: Dict[str, str], create: bool = True):
        self.camera_config = camera_config
        try:
            self.memory = self._load_memory_from_config(camera_config, create=create)
        except FileNotFoundError:
            raise ValueError(f"Shared memory with name {camera_config['name']} not found.")
        self._i = 0
        self._n_frames = int(camera_config["n_shmem_frames"])


    def _load_memory_from_config(self, config: Dict[str, str], create: bool=True) -> shared_memory.SharedMemory:
        image_shape = (
            int(config['n_shmem_frames']),
            int(config['height']),
            int(config['width']),
            int(config['channel'])
        )
        dtype = np.dtype(config['dtype'])
        n_bytes = int(np.prod(image_shape)) * dtype.itemsize
        self.shm = shared_memory.SharedMemory(create=create, name=config['name'], size=n_bytes)
        self.buffer = np.ndarray(
             image_shape,
            dtype=dtype,
            buffer=self.shm.buf
        )
        print(f"SharedImageList initialized with {config['n_shmem_frames']} frames of shape {image_shape} and dtype {dtype}.")
        return self.shm

    def get_new_frame(self) -> np.ndarray:
        img = self.buffer[self._i]
        self._i = (self._i + 1) % self._n_frames
        return img

    def at(self, i) -> np.ndarray:
        return self.buffer[i]

    @property 
    def current_index(self) -> int:
        return self._i
        