import sql
import tkinter as tk
from tkinter import messagebox, simpledialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

selected = []
num_to_month = {1 : 'January', 2 : 'February', 3 : 'March', 4 : 'April', 5 : 'May', 6 : 'June', 7 : 'July', 8 : 'August', 9 : 'September', 10 : 'October', 11 : 'November', 12 : 'December'}
month_to_num = {'January' : 1, 'February' : 2, 'March' : 3, 'April' : 4, 'May' : 5, 'June' : 6, 'July' : 7, 'August' : 8, 'September' : 9, 'October' : 10, 'November' : 11, 'December' : 12}

def handle_months(event):
  if not years_list.curselection():
    return
  
  if (len(selected) >= 1):
    selected[0] = years_list.get(years_list.curselection()[0])
  else:
    selected.append(years_list.get(years_list.curselection()[0]))
  
  months = sql.retrieve_months(selected[0])

  days_list.delete(0, tk.END)
  months_list.delete(0, tk.END)

  for month in months:
    months_list.insert(tk.END, num_to_month[month])

def handle_days(event):
  if not months_list.curselection():
    return
  
  if (len(selected) >= 2):
    selected[1] = months_list.get(months_list.curselection()[0])
  else:
    selected.append(months_list.get(months_list.curselection()[0]))

  days = sql.retrieve_days(month_to_num[selected[1]],selected[0])

  days_list.delete(0, tk.END)

  for day in days:
    days_list.insert(tk.END, day)
 
def handle_activities(event):
  if not days_list.curselection():
    return
  
  root.columnconfigure(2, weight=1)
  empty_frame(graph_frame)
  
  if (len(selected) >= 3):
    selected[2] = days_list.get(days_list.curselection()[0])
  else:
    selected.append(days_list.get(days_list.curselection()[0]))

  fig = Figure(figsize=(5, 4), dpi=100)
  ax = fig.add_subplot(111)
  fig.patch.set_facecolor('grey')
  
  activities = sql.retrieve_activities(selected[2],month_to_num[selected[1]],selected[0])

  categories = []
  values = []

  for activity,duration in activities:
    categories.append(activity)
    values.append(float(duration))
  
  ax.bar(categories, values, color='blue')

  ax.set_title(f'Activities for {selected[2]} of {selected[1]} for year {selected[0]}')
  ax.set_ylabel('Duration (hours)')
  ax.set_xlabel('Activity')

  canvas = FigureCanvasTkAgg(fig, graph_frame)
  canvas.draw()
  canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
  graph_frame.grid(row=0, column=2, sticky="nsew")

def empty_frame(frame):
  for widget in frame.winfo_children():
    widget.destroy()

def show_entry_frame():
    root.grid_columnconfigure(0, weight=1)
    entry_frame.grid(row=0, column=0, sticky="nsew")

def add_log():
  year = simpledialog.askinteger("Input", "Enter a year")
  month = simpledialog.askinteger("Input", "Enter a month (numerical)")
  day = simpledialog.askinteger("Input", "Enter a day")
  activity = simpledialog.askstring("Input", "Enter an activity")
  duration = simpledialog.askfloat("Input", "Enter the duration of the activity (hours)")

  if (year < 1900):
    messagebox.showwarning("Warning", "I don't do logs for vampires.")
    return

  if (month < 1 or month > 12):
    messagebox.showwarning("Warning", "Invalid month input")
    return
  
  if (day < 0 or day > 31):
    messagebox.showwarning("Warning", "Invalid day input")
    return

  if (duration < 0 or duration > 24):
    messagebox.showwarning("Warning", "Invalid duration input")
    return

  check = True

  years = sql.retrieve_years()
  for y in years:
    if (year == y):
      check = False
      break

  if (check):
    input = messagebox.askquestion("Confirm", "The year does not exist. Would you like to add it?")
    if input == "yes":
      sql.add_year(year)
    else:
      return
    
  check = True
  
  months = sql.retrieve_months(year)
  for m in months:
    if (month == m):
      check = False
      break
  
  if (check):
    input = messagebox.askquestion("Confirm", "The month does not exist. Would you like to add it?")
    if input == "yes":
      sql.add_month(month,year)
    else:
      return
  
  check = True
  
  days = sql.retrieve_days(month,year)

  for d in days:
    if (day == d):
      check = False
      break
  
  if (check):
    input = messagebox.askquestion("Confirm", "The day does not exist. Would you like to add it?")
    if input == "yes":
      sql.add_day(day,month,year)
    else:
      return
  
  sql.add_activity(day,month,year,activity,duration)

  messagebox.showinfo("Success")

root = tk.Tk()
root.title("The Daily Average")
root.geometry("500x500")

root.grid_columnconfigure(0, weight=0)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2,weight=0)
root.grid_rowconfigure(0, weight=1)

main_frame = tk.Frame(root, bg="lightblue")
graph_frame = tk.Frame(root, bg="gray")

for i in range(5):
  main_frame.grid_columnconfigure(i, weight=1)

for i in range(4):
  main_frame.grid_rowconfigure(i, weight=1)


#widgets on main frame
main_label = tk.Label(main_frame, text="The Daily Average", font=("Arial", 20), bg="lightblue")

add_entry = tk.Button(main_frame, text="Add New Entry", command=lambda: add_log())

year_label = tk.Label(main_frame, text="Years", bg="lightblue", font=("Arial", 12))
month_label = tk.Label(main_frame, text="Months", bg="lightblue", font=("Arial", 12))
day_label = tk.Label(main_frame, text="Days", bg="lightblue", font=("Arial", 12))

years_list = tk.Listbox(main_frame)
months_list = tk.Listbox(main_frame)
days_list = tk.Listbox(main_frame)

years = sql.retrieve_years()

for year in years:
  years_list.insert(tk.END, year)

main_label.grid(row=0, column=2, pady=20, sticky="news")
add_entry.grid(row=1, column=2, padx=5, sticky="ew")

year_label.grid(row=2, column=1, padx=5)
month_label.grid(row=2, column=2, padx=5)
day_label.grid(row=2, column=3, padx=5)

years_list.grid(row=3, column=1, padx=5, sticky='n')
months_list.grid(row=3, column=2, padx=5, sticky='n')
days_list.grid(row=3, column=3, padx=5, sticky='n')

main_frame.grid(row=0,column=1, sticky="nsew")

years_list.bind('<<ListboxSelect>>', handle_months)
months_list.bind('<<ListboxSelect>>', handle_days)
days_list.bind('<<ListboxSelect>>', handle_activities)

root.mainloop()




    