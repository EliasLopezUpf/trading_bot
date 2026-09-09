from abc import ABC, abstractmethod


class Exchange(ABC):

    @abstractmethod
    def get_order_book(self, symbol):
        pass
    
    @abstractmethod
    def supports_symbol(self, symbol):
        pass