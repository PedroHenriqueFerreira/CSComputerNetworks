class Actuator:
    def __init__(
        self, 
        is_active: bool = False,
    ):
        self.id = id(self)
        self.is_active = is_active
        
    def toggle(self):
        self.is_active = not self.is_active