class Car:
    top_speed = 100

    def __init__(self, starting_top_speed=100):
        self.top_speed = starting_top_speed
        self.__warnings = []

    def drive(self):
        print(f"I am driving, but less than {self.top_speed}")

    def add_warning(self, warning_text):
        self.__warnings.append(warning_text)

    def get_warnings(self):
        print(self.__warnings)

    def brag(self):
        print("I LOVE MY CAAAARRR")
# __dict__ -> prints field of objects :)
# __str__
# __repr__


car_1 = Car()
car_1.drive()

car_1.add_warning("warming")
car_1.get_warnings()
car_2 = Car(666)
car_2.drive()
# print(f'{car_2.warnings}')

car_3 = Car(555)
car_3.drive()
