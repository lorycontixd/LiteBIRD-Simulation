#Error class
from modules import utils
import logging
from datetime import datetime

logging.basicConfig(filename = "outputs/logs.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s -- %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)



class Error(Exception):
    """Base class for exceptions in this module."""
    def __init__(self):
        self.message = None
        self.errorlogger = logging.getLogger()
    
    def __str__(self):
        if self.message is not None:
            self.errorlogger.warning(self.message)
            return str(self.message)

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        super().__init__()
        self.expression = expression
        self.message = message

class TransitionError(Error):
    """Raised when an operation attempts a state transition that's not
    allowed.

    Attributes:
        previous -- state at beginning of transition
        next -- attempted new state
        message -- explanation of why the specific transition is not allowed
    """

    def __init__(self, previous, next, message):
        super().__init__()
        self.previous = previous
        self.next = next
        self.message = message

class SizeError(Error):
    """Raised when a quantity is not the size it should be.

    Attributes:
        quantity - the quantity whose size is wrong
        expected - the expected size of the quantity
        actual - the actual size of the quantity 
    """
    
    def __init__(self, previous, next, message):
        super().__init__()
        self.previous = previous
        self.next = next
        self.message = message
