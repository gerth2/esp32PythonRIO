from _private.webInterface import WS

class SmartDashboard:
    """
    Puts numbers to plots on a dashboard
    """
    def __init__(self):
        pass

    @staticmethod
    def putNumber(keyName: str, value):
        """
        Maps the specified key to the specified value in this table.
        
        The value can be retrieved by calling the get method with a key that is
        equal to the original key.
        
        :param keyName: the key
        :param value:   the value
        
        """
        WS.plotsPutNumber(keyName, value)