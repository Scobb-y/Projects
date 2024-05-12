import mysql.connector
from tkinter import simpledialog, messagebox

def createDatabase():
  try:
    conn = mysql.connector.connect(
      host="localhost",
      user=userID,
      password=passwordID
    )
    cursor = conn.cursor()
    cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s", ("averages",))
    result = cursor.fetchone()
    if result is not None:
      return
    else:
      cursor.execute("CREATE DATABASE IF NOT EXISTS averages")
      conn.database = "averages"
      cursor.execute("""
                    CREATE TABLE IF NOT EXISTS years (
                        year_id INT AUTO_INCREMENT PRIMARY KEY,
                        year INT NOT NULL,
                        UNIQUE(year)          
                          )
                    """)

      cursor.execute("""
                      CREATE TABLE IF NOT EXISTS months (
                        month_id INT AUTO_INCREMENT PRIMARY KEY,
                        year_id INT NOT NULL,
                        month INT NOT NULL,
                        FOREIGN KEY (year_id) REFERENCES years(year_id),
                        UNIQUE(year_id,month)
                      )
                    """)

      cursor.execute("""
                      CREATE TABLE IF NOT EXISTS days (
                        day_id INT AUTO_INCREMENT PRIMARY KEY,
                        month_id INT NOT NULL,
                        day INT NOT NULL,
                        FOREIGN KEY (month_id) REFERENCES months(month_id),
                        UNIQUE(month_id, day)
                      )
                    """)

      cursor.execute("""
                      CREATE TABLE IF NOT EXISTS activities (
                        activity_id INT AUTO_INCREMENT PRIMARY KEY,
                        day_id INT NOT NULL,
                        activity VARCHAR(255),
                        duration DECIMAL(5,2),
                        FOREIGN KEY (day_id) REFERENCES days(day_id)
                      )
      """)

  except mysql.connector.Error as e:
    print(f"An error occurred: {e}")

userID = None
passwordID = None

def getUser():
  while True:
    userID = simpledialog.askstring("User", "Enter your user-id")
    passwordID = simpledialog.askstring("User", "Enter your password")

    if userID is None or passwordID is None:
      messagebox.showinfo("Info", "No input provided for user or password. Failed attempt to connect.")
      return None, None
    
    try:
      conn = mysql.connector.connect(
        host="localhost",
        user=userID,
        password=passwordID
      )
      conn.close()
      return userID, passwordID
    
    except mysql.connector.Error as e:
      messagebox.showerror("Error", f"Failed to connect to database: {e}")
      retry = messagebox.askyesno("Retry", "Would you like to login again?")
      if not retry:
        return None, None

userID, passwordID = getUser()

createDatabase()

def add_year(year):
  try:
    conn = mysql.connector.connect(
      host="localhost",
      user=userID,
      password=passwordID,
      database="averages"
    )
    cursor = conn.cursor()
    query = "INSERT INTO years (year) VALUES (%s)"
    cursor.execute(query, (year,))
    conn.commit()
    print("Added year successfully")

  except mysql.connector.Error as e:
    if e.errno == 1062:
      print(f"Year {year} already exists")
    else:
      print(f"An error occurred: {e}")     

  finally:
    if cursor is not None:
      cursor.close()

    if conn.is_connected():
      conn.close()

def add_month(month, year):
  try:
    conn = mysql.connector.connect(
      host="localhost",
      user=userID,
      password=passwordID,
      database="averages"
    )

    cursor = conn.cursor()
    query = "SELECT year_id FROM years WHERE year = %s"
    cursor.execute(query, (year,))

    result = cursor.fetchone()

    if result:
      year_id = result[0]
    else:
      print(f"Year {year} does not exist")
      return

    query = "INSERT INTO months (year_id, month) VALUES (%s, %s)"

    cursor.execute(query, (year_id, month))

    conn.commit()

    print("Added month successfully")
  
  except mysql.connector.Error as e:
    if e.errno == 1062:
      print(f"{month} for {year} already exists")
    else:
      print(f"An error has occurred: {e}")
  
  finally:
    if cursor is not None:
      cursor.close()
    if conn.is_connected():
      conn.close()

def add_day(day, month, year):
  try:
    conn = mysql.connector.connect(
      host="localhost",
      user=userID,
      password=passwordID,
      database="averages"
    )

    cursor = conn.cursor()

    query = "SELECT year_id FROM years WHERE year = %s"
    cursor.execute(query, (year,))
    result = cursor.fetchone()
    
    if not result:
      print(f"Year {year} does not exist")
      return
    
    year_id = result[0]

    query = "SELECT month_id FROM months WHERE year_id = %s AND month = %s"
    cursor.execute(query, (year_id, month))
    result = cursor.fetchone()

    if not result:
      print(f"Month {month} does not exist")
      return
    
    month_id = result[0]

    query = "INSERT INTO days (month_id, day) VALUES (%s, %s)"
    cursor.execute(query, (month_id, day))

    conn.commit()

    print("Added day successfully")

  except mysql.connector.Error as e:
    if e.errno == 1062:
      print(f"Day {day} already exists")
    else:
      print(f"An error has occurred: {e}")

  finally:
    if cursor is not None:
      cursor.close()
    
    if conn.is_connected():
      conn.close()
  
def add_activity(day, month, year, activity, duration):
  try:
    conn = mysql.connector.connect(
      host="localhost",
      user=userID,
      password=passwordID,
      database="averages"
    )
    cursor = conn.cursor()

    query = "SELECT year_id FROM years WHERE year = %s"
    cursor.execute(query, (year,))
    result = cursor.fetchone()
    
    if not result:
      print(f"Year {year} does not exist")
      return
    
    year_id = result[0]

    query = "SELECT month_id FROM months WHERE year_id = %s AND month = %s"
    cursor.execute(query, (year_id, month))
    result = cursor.fetchone()

    

    if not result:
      print(f"Month {month} does not exist")
      return
      
    month_id = result[0]

    query = "SELECT day_id FROM days WHERE month_id = %s AND day = %s"
    cursor.execute(query, (month_id, day))
    result = cursor.fetchone()

    if not result:
      print(f"Day {day} does not exist")
    
    day_id = result[0]

    #Check if the activities duration sum does not exceed 24 (hours)
    query = "SELECT SUM(duration) FROM activities WHERE day_id = %s"
    cursor.execute(query, (day_id,))
    duration_total = cursor.fetchone()[0] or 0

    if float(duration_total) + duration > 24:
      print("Activities duration exceeds the daily limit of 24 hours")
      return

    query = "INSERT INTO activities (day_id, activity, duration) VALUES (%s, %s, %s)"
    cursor.execute(query, (day_id, activity, duration))

    conn.commit()

    print(f"Activity added to logs")
    

  except mysql.connector.Error as e:
    print(f"An error occurred: {e}")

  finally:
    if cursor is not None:
      cursor.close()
    
    if conn.is_connected():
      conn.close()

def retrieve_years():
  try:
      conn = mysql.connector.connect(
        host="localhost",
        user=userID,
        password=passwordID,
        database="averages"
      )
      cursor = conn.cursor()
      query = "SELECT year FROM years ORDER BY year ASC"
      cursor.execute(query)

      years = []

      for year in cursor.fetchall():
        years.append(year[0])
      
      return years
  
  except mysql.connector.Error as e:
    print(f"An error occurred: {e}")

  finally:
    if cursor is not None:
      cursor.close()
    
    if conn.is_connected():
      conn.close()

def retrieve_months(year):
  try:
      conn = mysql.connector.connect(
        host="localhost",
        user=userID,
        password=passwordID,
        database="averages"
      )

      cursor = conn.cursor()

      query = """
              SELECT m.month
              FROM months m
              JOIN years y ON m.year_id = y.year_id
              WHERE y.year = %s
              ORDER BY m.month ASC
              """
  
      cursor.execute(query, (year,))

      months = []

      for month in cursor.fetchall():
        months.append(month[0])

      return months
  
  except mysql.connector.Error as e:
    print(f"An error occurred: {e}")

  finally:
    if cursor is not None:
      cursor.close()
    
    if conn.is_connected():
      conn.close()

def retrieve_days(month, year):
  try:
      conn = mysql.connector.connect(
        host="localhost",
        user=userID,
        password=passwordID,
        database="averages"
      )

      cursor = conn.cursor()

      query = """
              SELECT d.day
              FROM days d
              JOIN months m ON d.month_id = m.month_id
              JOIN years y ON m.year_id = y.year_id
              WHERE y.year = %s AND m.month = %s
              ORDER BY d.day ASC
              """
  
      cursor.execute(query, (year,month))
      
      days = []

      for day in cursor.fetchall():
        days.append(day[0])

      return days
  
  except mysql.connector.Error as e:
    print(f"An error occurred: {e}")

  finally:
    if cursor is not None:
      cursor.close()
    
    if conn.is_connected():
      conn.close()

def retrieve_activities(day, month, year):
  try:
    conn = mysql.connector.connect(
      host="localhost",
      user=userID,
      password=passwordID,
      database="averages"
    )
    cursor = conn.cursor()

    query = """
            SELECT a.activity, a.duration
            FROM activities a
            JOIN days d ON a.day_id = d.day_id
            JOIN months m ON d.month_id = m.month_id
            JOIN years y ON m.year_id = y.year_id
            WHERE y.year = %s AND m.month = %s and d.day = %s
            ORDER BY a.activity ASC
            """
    cursor.execute(query, (year, month, day))

    activities = []

    for activity in cursor.fetchall():
      activities.append(activity)
    
    return activities

  except mysql.connector.Error as e:
    print(f"An error has occurred: {e}")

  finally:
    if cursor is not None:
      cursor.close()
    
    if conn.is_connected():
      conn.close()

def add_durations(activities):
  totals = {'total' : 0.00}
  for activity, duration in activities:
    totals['total'] += float(duration)
    if activity in totals:
      totals[activity] += float(duration)
    else:
      totals[activity] = float(duration)
  
  return totals
    
