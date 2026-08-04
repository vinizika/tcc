from abc import ABC, abstractmethod


class BaseClient(ABC):

    @abstractmethod
    def health(self):
        pass