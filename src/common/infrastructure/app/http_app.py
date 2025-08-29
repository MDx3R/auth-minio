from abc import abstractmethod

from common.infrastructure.app.app import IApp


class IHTTPApp(IApp):
    def configure(self):
        self.configure_dependencies()
        self.register_routers()

    @abstractmethod
    def configure_dependencies(self): ...

    @abstractmethod
    def register_routers(self) -> None: ...
