from _private.Controllers import KB

class Keyboard:
    """
    A class to handle keyboard input for the robot.
    It provides methods to check if specific keys are pressed.
    """
    def __init__(self):
        """
        Initializes the Keyboard class.
        """
        pass
    def w_pressed(self):
        """
        Checks if the 'W' key is pressed.
        
        :return: True if 'W' is pressed, False otherwise.
        """
        return KB.w()
    def a_pressed(self):
        """
        Checks if the 'A' key is pressed.
        
        :return: True if 'A' is pressed, False otherwise.
        """
        return KB.a()
    def s_pressed(self):
        """
        Checks if the 'S' key is pressed.
        
        :return: True if 'S' is pressed, False otherwise.
        """
       
        return KB.s()
    def d_pressed(self):
        """
        Checks if the 'D' key is pressed.
        
        :return: True if 'D' is pressed, False otherwise.
        """
       
        return KB.d()
    def q_pressed(self):
        """
        Checks if the 'Q' key is pressed.
        
        :return: True if 'Q' is pressed, False otherwise.
        """
       
        return KB.q()
    def e_pressed(self):
        """
        Checks if the 'E' key is pressed.
        
        :return: True if 'E' is pressed, False otherwise.
        """
       
        return KB.e()
    def z_pressed(self):
        """
        Checks if the 'Z' key is pressed.
        
        :return: True if 'Z' is pressed, False otherwise.
        """
       
        return KB.z()
    def x_pressed(self):
        """
        Checks if the 'X' key is pressed.
        
        :return: True if 'X' is pressed, False otherwise.
        """
       
        return KB.x()
    def c_pressed(self):
        """
        Checks if the 'C' key is pressed.
        
        :return: True if 'C' is pressed, False otherwise.
        """
       
        return KB.c()
