import json
import bcrypt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


# -------------------------
# USER MANAGEMENT
# -------------------------
class UserManager:
    def __init__(self, file="users.json"):
        self.file = file
        self.data = self.load_data()

    def load_data(self):
        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except:
            return {}

    def save_data(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=4)

    def signup(self, username, password):
        if username in self.data:
            print("User already exists")
            return False
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self.data[username] = {"password": hashed, "tests": []}
        self.save_data()
        return True

    def login(self, username, password):
        if username not in self.data:
            return False
        stored = self.data[username]["password"].encode()
        return bcrypt.checkpw(password.encode(), stored)


# -------------------------
# DATA MANAGEMENT
# -------------------------
class DataManager:
    def __init__(self, user_manager, username):
        self.um = user_manager
        self.username = username

    def add_test(self, test):
        self.um.data[self.username]["tests"].append(test)
        self.um.save_data()

    def get_dataframe(self):
        tests = self.um.data[self.username]["tests"]
        if not tests:
            return pd.DataFrame()

        df = pd.DataFrame(tests)
        df.rename(columns={"test_name": "Exam", "test_date": "Date"}, inplace=True)
        df["Date"] = pd.to_datetime(df["Date"], format='%d/%m/%y')
        return df.sort_values("Date")


# -------------------------
# ANALYSIS + ML
# -------------------------
class Analyzer:
    def __init__(self, df):
        self.df = df
        self.subjects = ["Physics", "Chemistry", "Maths"]

    def compare(self, index):
        if self.df.empty or index >= len(self.df):
            print("Invalid data")
            return

        past = self.df.loc[index, self.subjects]
        latest = self.df.iloc[-1][self.subjects]

        print("Percentage change:")
        print(((latest - past) / past) * 100)

    def plot(self, index):
        past = self.df.loc[index, self.subjects]
        latest = self.df.iloc[-1][self.subjects]

        x = np.arange(len(self.subjects))
        width = 0.3

        plt.bar(x - width/2, past, width, label="Past")
        plt.bar(x + width/2, latest, width, label="Latest")

        plt.xticks(x, self.subjects)
        plt.legend()
        plt.show()

    def predict(self):
        if len(self.df) < 4:
            print("Need at least 4 tests")
            return

        X = np.array([1,2,3,4]).reshape(-1,1)
        y = self.df[self.subjects].tail(4).values

        model = LinearRegression().fit(X, y)
        pred = model.predict([[5]])

        return dict(zip(self.subjects, pred[0]))


# -------------------------
# MAIN APP
# -------------------------
class StudentApp:
    def __init__(self):
        self.um = UserManager()

    def run(self):
        username = input("Username: ")
        password = input("Password: ")

        if not self.um.login(username, password):
            print("User not found. Creating new user...")
            self.um.signup(username, password)

        dm = DataManager(self.um, username)

        while True:
            print("\n1. Add Test\n2. Compare\n3. Graph\n4. Predict\n5. Exit")
            choice = input("Choice: ")

            if choice == "1":
                test = {
                    "test_name": input("Test Name: "),
                    "test_date": input("Date (DD/MM/YY): "),
                    "Physics": int(input("Physics: ")),
                    "Chemistry": int(input("Chemistry: ")),
                    "Maths": int(input("Maths: "))
                }
                dm.add_test(test)

            elif choice == "2":
                df = dm.get_dataframe()
                Analyzer(df).compare(int(input("Index: ")))

            elif choice == "3":
                df = dm.get_dataframe()
                Analyzer(df).plot(int(input("Index: ")))

            elif choice == "4":
                df = dm.get_dataframe()
                print(Analyzer(df).predict())

            elif choice == "5":
                break


if __name__ == "__main__":
    StudentApp().run()