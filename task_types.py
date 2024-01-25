from enum import Enum
import pandas as pd

class Gender(Enum):
    male = 0
    female = 1

# Activity_level 
# "1" : "BMR",
# "2" : "Sedentary: little or no exercise",
# "3" : "Exercise 1-3 times/week",
# "4" : "Exercise 4-5 times/week",
# "5" : "Daily exercise or intense exercise 3-4 times/week",
# "6" : "Intense exercise 6-7 times/week",
# "7" : "Very intense exercise daily, or physical job" 
    
class Goal(Enum):
    maintain = 0
    mildlose = 1
    weightlose = 2
    extremelose = 3
    mildgain = 4
    weightgain = 5
    extremegain = 6

class Human_params:
    def __init__(self, age, gender: Gender, height, weight, activitylevel, goals: Goal):
        self._age = age
        self._gender = gender
        self._height = height
        self._weight = weight
        self._activitylevel = activitylevel
        self._goals = goals

    def get_dict(self) -> dict:
        d = {
            'age': self._age, 
            'gender': self._gender.name, 
            'height': self._height,
            'weight': self._weight,
            'activitylevel': self._activitylevel,
            'goal': self._goals.name
        }
        return d

    def get_df(self):
        dictt = self.get_dict()
        return pd.DataFrame(dictt, index=[0])