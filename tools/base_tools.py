from abc import ABC, abstractmethod

class Tool(ABC):
    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    @abstractmethod
    def getName(self) -> str:
        pass

    @abstractmethod
    def getDescription(self) -> str:
        pass

    @abstractmethod
    def getParameters(self) -> dict:
        pass