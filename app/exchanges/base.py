from abc import ABC, abstractmethod


class Exchange(ABC):

    @abstractmethod
    def get_order_book(self, symbol):
        pass
    
    @abstractmethod
    def supports_symbol(self, symbol):
        pass
    
    @abstractmethod
    async def stream_order_books(self, symbols):
        pass
    
    @abstractmethod
    async def initialize_order_book(self,symbol,queue,local_book):
        pass
    
    @abstractmethod
    def process_order_book_update(self,update,local_book):
        pass
    
    @abstractmethod
    def uses_sequence_numbers(self):
        pass
    
    @abstractmethod
    def get_symbol_from_update(self, update):
        pass