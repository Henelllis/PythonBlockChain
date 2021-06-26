class Bus:
    top_speed = 100

    def __init__(self, starting_top_speed=100):
        self.top_speed = starting_top_speed
        self.__warnings = []
        self.pessengers = []

    def drive(self):
        print(f"I am driving, but less than {self.top_speed}")

    def add_warning(self, warning_text):
        self.__warnings.append(warning_text)

    def get_warnings(self):
        print(self.__warnings)

    def add_group(self, passengers):
        self.pessengers.extend(passengers)


bus1 = Bus(100)
bus1.add_group(['a', 'b', 'c'])
print(bus1.pessengers)
