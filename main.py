import json
import bcrypt as pt
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as pl
# Check or load user file
def check_user_file():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# User login
def user_login(username, password):
    data = check_user_file()
    if username in data:
        password_bytes = password.encode('utf-8')
        storedhash = data[username]["password"].encode('utf-8')
        if pt.checkpw(password_bytes, storedhash):
            print("Login Successful")
            return True
        else:
            # Return 'try' specifically when password does not match
            return "try"
    else:
        print("Username not found.")
        return False

# User signup
def user_signup(username):
    data = check_user_file()
    if username in data:
        print("User already exists. Please login.")
        return False
    else:
        choice = input("You don't have an ID. Do you want to create one? (Yes/No): ")
        if choice.lower() == "yes":
            password = input("Enter your password: ")
            storedhash = pt.hashpw(password.encode('utf-8'), pt.gensalt(rounds=12))
            storedhash = storedhash.decode('utf-8') # Store as string
            data[username] = {"password": storedhash, "tests": []}
            with open("users.json", "w") as file:
                json.dump(data, file, indent=4)
            print("User created successfully!")
            return True
        else:
            print("Signup cancelled.")
            return False

# Add test data for user
def take_user_data(username):
    data = check_user_file()
    if username not in data:
        print("User not found.")
        return

    Test_date = input("Please enter your test date (DD/MM/YY): ")
    Test_Name = input("Enter the name of your test: ")
    Physics = int(input("Enter your marks in Physics: "))
    Chemistry = int(input("Enter your marks in Chemistry: "))
    Maths = int(input("Enter your marks in Maths: "))

    userdatadict = {
        "test_name": Test_Name,
        "test_date": Test_date,
        "Physics": Physics,
        "Chemistry": Chemistry,
        "Maths": Maths
    }

    data[username]["tests"].append(userdatadict)

    with open("users.json", "w") as file:
        json.dump(data, file, indent=4)
    print("The data is successfully updated!")

# For data Frame
def pandas_dataframe(username):
    data=check_user_file()
    if data=={}:
        print("No data found")
        return pd.DataFrame() # Return empty DataFrame if no data
    if username not in data or "tests" not in data[username]:
        print(f"No test data found for user {username}")
        return pd.DataFrame()

    to_display=data[username]["tests"]
    df = pd.DataFrame(to_display)
    df.rename(columns={"test_name":"Exam-Name","test_date":"Date-of-Exam"},inplace=True)
    df["Date-of-Exam"]=pd.to_datetime(df["Date-of-Exam"], format='%d/%m/%y', errors='coerce') # Specify format
    df = df.sort_values(by="Date-of-Exam").reset_index(drop=True)
    print(df)
    return df

# useranalysisfunction
def useranalysis(username,numberoftest):
    df=pandas_dataframe(username)
    if df.empty:
        print("Cannot perform analysis: No data to analyze.")
        return None, None

    subjects = ["Physics", "Chemistry", "Maths"]
    try:
        if numberoftest < 0 or numberoftest >= len(df):
            print(f"Error: Test number {numberoftest} is out of bounds. Please enter a valid test index (0 to {len(df)-1}).")
            return None, None

        past_test=df.loc[numberoftest,subjects]
        latest_test=df.iloc[-1][subjects]
        percentage=((-past_test+latest_test)/past_test)*100
        print("THE Percentage increase from last test is :",percentage)
        list_of_increase=[]
        i=0
        while i<len(subjects):
            past_test_subjects=df.loc[numberoftest,subjects[i]]
            # Fixed: Access the specific subject directly from the Series
            latest_test_subjects=df.iloc[-1][subjects[i]]
            markschange=latest_test_subjects-past_test_subjects
            if markschange>=0:
                list_of_increase.append(f"The increase in marks in {subjects[i]}:{markschange}")
            elif markschange<0:
                list_of_increase.append(f"The decrease in marks in {subjects[i]}:{markschange}")
            print(list_of_increase[i])
            i+=1
        return past_test , latest_test
    except Exception as e:
        print(f"An error Occurred:{e}")
        return None, None

#now finally matplotlib for visualization
def graph_visualization(username,numberoftest):
    past_test,latest_test=useranalysis(username,numberoftest)
    if past_test is None or latest_test is None:
        print("Cannot visualize due to error in user analysis.")
        return

    Subjects=["Physics","Chemistry","Maths"]
    width=0.35
    df=pandas_dataframe(username)
    x=np.arange(len(Subjects))
    fig,ax=pl.subplots(figsize=(8,6))
    plot1=ax.bar(x-width/2,past_test,width,label=df.iloc[numberoftest]["Exam-Name"],color='#4a90e2')
    plot2=ax.bar(x+width/2,latest_test,width,label=df.iloc[-1]["Exam-Name"],color='#ff6b6b')
    ax.set_ylabel('Marks')
    ax.set_title('Side by Side comparison of the marks of both tests')
    ax.set_xticks(x)
    ax.set_xticklabels(Subjects)
    ax.legend()
    ax.bar_label(plot1, padding=3)
    ax.bar_label(plot2, padding=3)
    pl.show()

def linear_regression(df):
    # Ensure the DataFrame has enough rows
    if len(df) < 4:
        print("Not enough data for linear regression. Need at least 4 tests.")
        return None

    X = np.array([1, 2, 3, 4]).reshape(-1, 1) # Represent test order (1st, 2nd, 3rd, 4th latest)

    # Use the last 4 tests from the provided DataFrame
    y = np.array([
        [df.iloc[-4]["Physics"],df.iloc[-4]["Chemistry"] ,df.iloc[-4]["Maths"] ],
        [df.iloc[-3]["Physics"],df.iloc[-3]["Chemistry"] ,df.iloc[-3]["Maths"] ],
        [df.iloc[-2]["Physics"],df.iloc[-2]["Chemistry"] ,df.iloc[-2]["Maths"] ],
        [df.iloc[-1]["Physics"],df.iloc[-1]["Chemistry"] ,df.iloc[-1]["Maths"] ]
    ])

    model = LinearRegression().fit(X, y)

    test_5 = np.array([[5]]) # Predict for the next test (5th in sequence)
    subjects = ["Physics", "Chemistry", "Maths"]
    prediction=model.predict(test_5)
    predicted=dict(zip(subjects, prediction[0]))
    df_prediction=pd.DataFrame([predicted])
    return df_prediction

#the main function
def main(username,password):
    login_status = user_login(username, password)
    logged_in = False

    if login_status is True:
        logged_in = True
    elif login_status is False: # Username not found
        print("Username not found. Offering to sign up.")
        if user_signup(username): # If signup is successful
            logged_in = True
    elif login_status == "try": # Password incorrect, allow retries
        attempts = 1
        max_attempts = 5
        while attempts < max_attempts:
            password = input(f"Password incorrect. Enter your password again (Attempt {attempts + 1}/{max_attempts}): ")
            login_status = user_login(username, password)
            if login_status is True:
                logged_in = True
                break
            elif login_status is False: # Should not happen if initial login_status was 'try' and username exists
                print("An unexpected error occurred during password retries (username might have been deleted).")
                break
            attempts += 1
        if not logged_in: # If all attempts failed
            print(f"Maximum login attempts ({max_attempts}) reached. Offering to sign up.")
            if user_signup(username):
                logged_in = True

    if not logged_in: # If after all attempts and signup, user is still not logged in
        print("Exiting application as login/registration failed or was cancelled.")
        return

    # If logged_in is True, proceed to the menu
    print("1.Comapre your current test with a previous test ?\n")
    print("2.Want to enter new data?\n")
    print("3.Want to see a graph comparison of previous and latest test?\n")
    print("4.Predict the marks of next test based on the last 4 ?")
    print("5.Exit")
    choiceofmain=None
    while choiceofmain!=5:
      df = pandas_dataframe(username)
      if df.empty:
          print("No test data available for options 1, 3, 4. Please enter new data (option 2).")
          # If there is no data, only allow option 2 or 5
          if choiceofmain != 2 and choiceofmain != 5:
              try:
                  choiceofmain=int(input(":::::")) # Re-prompt for input if invalid choice with empty df
                  continue # Go back to loop start to re-check df.empty
              except ValueError:
                  print("Enter a valid value")
                  continue

      try:
          choiceofmain=int(input(":::::"))
          if choiceofmain==1:
              numberoftest=int(input("Enter the index of the test you want to compare with (0-indexed):"))
              useranalysis(username,numberoftest)
          elif choiceofmain==2:
              take_user_data(username)
          elif choiceofmain==3:
              numberoftest=int(input("Enter the index of the test you want to compare with (0-indexed):"))
              graph_visualization(username,numberoftest)
          elif choiceofmain == 4:
              if len(df) >= 4:
                  print(linear_regression(df)) # Pass the DataFrame directly
              else:
                  print(f"Not Enough data! You only have {len(df)} tests. Need at least 4 for prediction.")
      except ValueError:
        print("Enter a valid value")
    print("You have exited the window")
if __name__ == "__main__":
    username = input("Enter username: ")
    password = input("Enter password: ")
    main(username, password)
