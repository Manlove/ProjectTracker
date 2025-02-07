import sqlite3 as sql, tkinter as tk
from tkinter import ttk
from tkinter.filedialog import asksaveasfile
import re
from datetime import timedelta, datetime, time, date
from functools import partial

class Application(tk.Frame):

	def __init__(self, master  = None):
		# Create Main Window
		self.root = tk.Tk()
		self.root.title("Project Tracker")

		# When the user goes to close the program, run the on_close function to save the database before closing
		self.root.protocol("WM_DELETE_WINDOW", self.on_close)

		# Assign the root window as the master
		master = self.root
		super().__init__(master)

		# Load the time keeper database
		self.database = Project_Log()

		# Calls the build_page method to build the main application page.
		self.pack()
		self.build_page()

		# Applies the menu created in build_page to the menu bar
		self.root.config(menu = self.menu_bar)

	def on_close(self):
		''' When the user closes the program initiates the database.close() method to commit all changes to the database
			before closing the connection and terminating the application window.'''

		self.database.close()
		self.root.destroy()

	def build_page(self):

		try:
			self.main_frame.destroy()
		except:
			pass
		# Builds the file menu
		self.build_menu()

		# creates frames for the different section (To Do, Action Taken, Ready, On Hold)
		self.main_frame = tk.Frame(self)
		self.main_frame.grid(row = 0, column = 0, sticky = 'w')

		panes = []
		for i,j in zip([0,1,2,3], ["TO DO", "ACTION TAKEN", "READY", "ON HOLD"]):
			panes.append(Category(self, self.main_frame, self.database, title = j, position = i))

	def build_menu(self):
		''' builds the menu bar for the application and adds all the options to the bar'''

		# Set up the menu bar for the main application
		self.menu_bar = tk.Menu(self.root)

		# Creates a new menu cascade for file/user actions
		self.file_menu = tk.Menu(self.menu_bar, tearoff = 0)

		# Adds commands for saving, clearing the form, and activating and deactivating a user to the file menu tab
		self.file_menu.add_command(label = "Save", command = self.save_database)
		self.file_menu.add_command(label = "Add Project", command = self.add_project_window)
		self.file_menu.add_command(label = "New Day", command = self.reset_action_taken)

		# Names the cascade 'File' and and adds it to the menu bar
		self.menu_bar.add_cascade(label = "File", menu=self.file_menu)

	def save_database(self):
		''' Calls the database.save function to save the database'''
		self.database.save()

	def add_project_window(self):
		''' Creates a pop-out window for the project to enter the information to add a project
				This window has:
					1) An entry box for the project number
					2) An entry box for the quote number
					3) An entry box for the Insitute
					4) A drop down menu for the project type
					5) An entry box for the investigator
					6) An entry box for the email
					7) An entry box for the sales contact
					8) A button to add the project
		'''

		# Creates a new window, with the title add project
		self.new_project_window = tk.Toplevel()
		self.new_project_window.title("Add Project")

		# Creates a frame within this window to hold the entry widgets
		self.entry_frame = tk.Frame(self.new_project_window)
		self.entry_frame.grid(row = 0, column = 0)

		# Creates the labels for all the entry widgets
		tk.Label(self.entry_frame, text = "Project Number").grid(row = 0, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Quote Number").grid(row = 1, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Institute").grid(row = 3, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Project Type").grid(row = 2, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Investigator").grid(row = 4, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Email").grid(row = 5, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Sales Contact").grid(row = 6, column = 0, padx = 5, stick = "w")

		# Creates the two name entry widgets
		self.new_project_number = tk.Entry(self.entry_frame, width = 35)
		self.new_project_quote_number = tk.Entry(self.entry_frame, width = 35)

		# Creates a variable and the combobox for the role, populates the combobox with all possible roles
		self.new_project_type_variable = tk.StringVar()
		self.new_project_type = ttk.Combobox(self.entry_frame, textvariable = self.new_project_type_variable, width = 33)
		self.new_project_type['values'] = ['ChIP', 'ATAC', 'ATAC-val', 'RNA', 'RRBS', 'scATAC', 'scRNA', 'HiC']

		self.new_project_institute = tk.Entry(self.entry_frame, width = 35)
		self.new_project_investigator = tk.Entry(self.entry_frame, width = 35)
		self.new_project_email = tk.Entry(self.entry_frame, width = 35)
		self.new_project_sales = tk.Entry(self.entry_frame, width = 35)

		# Places all the entry widgets on the frame
		self.new_project_number.grid(row = 0, columnspan = 2, column = 1, pady = 5)
		self.new_project_quote_number.grid(row = 1, columnspan = 2, column = 1, pady = 5)
		self.new_project_type.grid(row = 2, columnspan = 2, column = 1, pady = 5)
		self.new_project_institute.grid(row = 3, columnspan = 2, column = 1, pady = 5)
		self.new_project_investigator.grid(row = 4, columnspan = 2, column = 1, pady = 5)
		self.new_project_email.grid(row = 5, columnspan = 2, column = 1, pady = 5)
		self.new_project_sales.grid(row = 6, columnspan = 2, column = 1, pady = 5)

		# Creates a frame for the button
		self.new_project_button_frame = tk.Frame(self.new_project_window)
		self.new_project_button_frame.grid(row = 1, column = 0)

		# Adds a button for the project to press to run the add_project function
		self.create_project_button = tk.Button(self.new_project_button_frame, text = "Add Project", width = 20, command = self.add_project)
		self.create_project_button.grid(row = 0, columnspan = 1, column = 0, pady = 5)

	def add_project(self):
		''' This is run when the button on the add_user_window page is pressed. It retrieves all the
			information in the entry widgets and checks to see if the three required fields
			(first name, last name, role) were filled. If they are not, notifies the user that
			the fields are required. If they are, adds the user to the database with the
			database.add_user function and updates the roles in the role selection widget before
			destroying the window'''

		# Retrieves the data from the four entry widgets and the one combobox selection widget
		# The four entry widget values are passed through the clean_input function
		project_number = self.clean_input(self.new_project_number.get())
		quote_number =  self.clean_input(self.new_project_quote_number.get())
		project_type = self.new_project_type.get()
		institute = self.clean_input(self.new_project_institute.get())
		investigator = self.clean_input(self.new_project_investigator.get())
		email = self.clean_input(self.new_project_email.get())
		sales_contact = self.clean_input(self.new_project_sales.get())

		# Checks to see that the first name, last name and role were not left empty
		if "" in [project_number, quote_number]:

		# If they were, prompts the user that the fields are required
			self.error_window("Please Enter Required Fields")

		# Otherwise, calls the database.add_user function to add the user
		else:
			self.database.add_project(project_number, quote_number, institute, project_type, investigator, email, sales_contact)

		# Destroys the add_user_window
			self.new_project_window.destroy()

		# Updates the current view
			self.build_page()

	def reset_action_taken(self):
		self.database.reset_action_taken()
		self.build_page()

	def clean_input(self, input):
		''' Used to do a brief sanitization of the inputs in the entry boxes
			as a basic prevention of sql injection attacks.
			Takes a string and returns the updated string.

			It is intended that only admins would be using the entry boxes.
			The general users would be selecting names/ roles and using spinboxes for time entries'''

		# replaces single and double quotes with spaces
		return re.sub(r'[\'\"]', ' ', input)

	def error_window(self, message, window_title = "Error"):
		''' Takes a message and the window tittle and creates a window to notify the user'''

		# Creates a window
		window  = tk.Toplevel()
		window.title(window_title)

		# creates a message on the window with the given string
		tk.Label(window, text = '{}'.format(message)).grid(row = 0,  column = 0, pady = 5, padx = 20)

		# Creates a button to allow the user to close the window.
		tk.Button(window, text = 'OK', width = 10, command = lambda :window.destroy()).grid(row = 1, column = 0, pady = 5)

class Project_Log():
	def __init__(self):
		""" connects to the Project_Log database, sets-up a database cursor and runs the setup method """

		self.conn = sql.connect("Project_Log")
		self.cursor = self.conn.cursor()
		self.setup()

	def close(self):
		self.conn.commit()
		self.conn.close()

	def save(self):
		self.conn.commit()

	def setup(self):
		'''Creates the project table if it does not exist with columns titled:
			projet_ID as primary key, quote number as integer, institute as text,
			project status as TEXT, investigator name as text, investigator email as text, start date as text, end date
			as text, the sales contact as text, the current action as text'''

		self.cursor.execute("CREATE TABLE IF NOT EXISTS projects (project_id_number integer PRIMARY KEY, project_ID TEXT, quote_number INTEGER, institute TEXT, type TEXT, project_status TEXT, investigator_name TEXT, investigator_email TEXT, start_date TEXT, end_date TEXT, sales_contact TEXT, current_action TEXT)")

	def add_project(self, project_ID, quote_number, institute, type, investigator = "NA", email = "NA", sales_contact = "NA"):
		start_date = date.today()
		self.cursor.execute("INSERT INTO projects (project_ID, quote_number, institute, type, project_status, investigator_name, investigator_email, start_date, end_date, sales_contact, current_action) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (project_ID, quote_number, institute, type, "TO DO", investigator, email, start_date, "NA", sales_contact, "Ready to start"))

	def get_by_status(self, status):
		projects_list = self.cursor.execute('''SELECT project_id_number, project_ID, quote_number, institute, type, project_status, current_action
											FROM projects
											WHERE project_status = ?''', (status,)).fetchall()
		return [i for i in projects_list]

	def update_status(self, id, status):
		if status == "DELIVERED":
			self.project_delivered(id)
		self.cursor.execute("UPDATE projects SET project_status = ? WHERE project_id_number = ?", (status, id))

	def update_action(self, id, action):
		self.cursor.execute("UPDATE projects SET current_action = ? WHERE project_id_number = ?", (action, id))

	def get_info(self, id):
		project_list = self.cursor.execute('''SELECT * FROM projects
											WHERE project_id_number = ?''', (id,)).fetchall()
		return project_list[0]

	def project_delivered(self, id):
		end_date = date.today()
		self.cursor.execute("UPDATE projects SET end_date = ? WHERE project_id_number = ?", (end_date, id))

	def reset_action_taken(self):
		self.cursor.execute("UPDATE projects SET project_status = 'TO DO' WHERE project_status = 'ACTION TAKEN'")
		return True


class Category():
	def __init__(self, tracker, frame, database, title, position):
		self.tracker = tracker
		self.title = title
		self.database = database
		self.action_frame = tk.Frame(frame)
		self.action_frame.grid(row = position, column = 0, sticky = 'w')

		self.label = tk.Label(self.action_frame, text = "[ {0} ]".format(title), font = 'Arial 18 bold')
		self.label.grid(row = 0, column = 0, sticky = 'w')

		self.project_frame = tk.Frame(self.action_frame)
		self.project_frame.grid(row = 1, column = 0)

		self.label = tk.Label(self.action_frame, text = "").grid(row = 2, column = 1)

		self.load_projects()

	def load_projects(self):
		projects = self.database.get_by_status(self.title)
		project_list = []
		for n,i in enumerate(projects):
			project_list.append(Project(self.tracker, self.database, n, self.project_frame, i[0], i[1], i[2], i[3], i[4], i[5], i[6]))

class Project():
	def __init__(self, tracker, database, placement, frame, project_number, ID, quote, institute, type, status, action):
		self.tracker = tracker
		self.database = database
		self.project_number = project_number
		self.ID = ID
		self.quote = quote
		self.institute = institute
		self.type = type
		self.status = status
		self.parent_frame = frame
		self.placement = placement
		self.current_action = action
		self.place_project()

	def place_project(self):
		self.frame = tk.Frame(self.parent_frame)
		self.frame.config(bg = "white")
		tk.Label(self.frame, text = self.ID, bg = "white").grid(row = 0, column = 0, padx = 10)
		tk.Label(self.frame, text = self.quote, bg = "white").grid(row = 0, column = 1, padx = 10)
		tk.Label(self.frame, text = self.institute, bg = "white").grid(row = 0, column = 2, padx = 10)
		tk.Label(self.frame, text = self.type, bg = "white").grid(row = 0, column = 3, padx = 10)
		tk.Label(self.frame, text = self.current_action, bg = "white").grid(row = 0, column = 4, padx = 10)
		self.option_button = tk.Menubutton(self.frame, text = "+", activebackground = 'blue')
		self.option_button.grid(row = 0, column = 5, padx = 10)
		self.option_button.menu = tk.Menu(self.option_button, tearoff = 0)
		self.option_button["menu"] = self.option_button.menu
		status_menu = tk.Menu(self.option_button, tearoff = 0)
		status_menu.add_command(label = "TO DO", command = partial(self.update_status, "TO DO"))
		status_menu.add_command(label = "ACTION TAKEN", command = partial(self.update_status, "ACTION TAKEN"))
		status_menu.add_command(label = "READY", command = partial(self.update_status, "READY"))
		status_menu.add_command(label = "ON HOLD", command = partial(self.update_status, "ON HOLD"))
		status_menu.add_command(label = "DELIVERED", command = partial(self.update_status, "DELIVERED"))

		action_menu = tk.Menu(self.option_button, tearoff = 0)
		action_menu.add_command(label = "Ready to start", command = partial(self.update_action, "Ready to start"))
		action_menu.add_command(label = "Running Alignment", command = partial(self.update_action, "Running Alignment"))
		action_menu.add_command(label = "Running Analysis", command = partial(self.update_action, "Running Analysis"))
		action_menu.add_command(label = "Ready to Package", command = partial(self.update_action, "Ready to Package"))
		action_menu.add_command(label = "Ready to Deliver", command = partial(self.update_action, "Ready to Deliver"))
		action_menu.add_command(label = "Downsampling", command = partial(self.update_action, "Downsampling"))
		action_menu.add_command(label = "More Info Required", command = partial(self.update_action, "More Info Required"))

		self.option_button.menu.add_separator()
		self.option_button.menu.add_cascade(label = "Update Status", menu = status_menu)
		self.option_button.menu.add_separator()
		self.option_button.menu.add_cascade(label = "Update Current Action", menu = action_menu)
		self.option_button.menu.add_separator()
		self.option_button.menu.add_command(label = "Get Info", command = self.info_window)
		self.option_button.menu.add_separator()

		self.frame.grid(row = self.placement, column = 0, sticky = "w")

	def info_window(self):

		# Creates a new window, with the title add project
		self.project_info_window = tk.Toplevel()
		self.project_info_window.title("Project Information")

		# Creates a frame within this window to hold the entry widgets
		self.entry_frame = tk.Frame(self.project_info_window)
		self.entry_frame.grid(row = 0, column = 0)

		project_info = self.database.get_info(self.project_number)

		# Creates the labels for all the entry widgets
		tk.Label(self.entry_frame, text = "Project Number").grid(row = 0, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Quote Number").grid(row = 1, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Project Type").grid(row = 2, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Project Status").grid(row = 3, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Current Action").grid(row = 4, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "").grid(row = 5, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Institute").grid(row = 6, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Investigator").grid(row = 7, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Email").grid(row = 8, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Sales Contact").grid(row = 9, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "").grid(row = 10, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "Start Date").grid(row = 11, column = 0, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "End Date").grid(row = 12, column = 0, padx = 5, stick = "w")

		tk.Label(self.entry_frame, text = project_info[1]).grid(row = 0, column = 1, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = project_info[2]).grid(row = 1, column = 1, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = project_info[4]).grid(row = 2, column = 1, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = project_info[5]).grid(row = 3, column = 1, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = project_info[11]).grid(row = 4, column = 1, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "").grid(row = 5, column = 1, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = project_info[3]).grid(row = 6, column = 1, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = project_info[6]).grid(row = 7, column = 1, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = project_info[7]).grid(row = 8, column = 1, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = project_info[10]).grid(row = 9, column = 1, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = "").grid(row = 10, column = 1, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = project_info[8]).grid(row = 11, column = 1, padx = 5, stick = "w")
		tk.Label(self.entry_frame, text = project_info[9]).grid(row = 12, column = 1, padx = 5, stick = "w")

		# Creates a frame for the button
		self.get_info_button_frame = tk.Frame(self.project_info_window)
		self.get_info_button_frame.grid(row = 1, column = 0)

		# Adds a button for the project to press to run the add_project function
		self.create_info_button = tk.Button(self.get_info_button_frame, text = "OK", width = 20, command = lambda :self.project_info_window.destroy())
		self.create_info_button.grid(row = 0, columnspan = 1, column = 0, pady = 5)

		self.project_info_window.grab_set()

	def update_status(self, status):
		self.database.update_status(self.project_number, status)
		self.tracker.build_page()

	def update_action(self, action):
		self.database.update_action(self.project_number, action)
		self.tracker.build_page()

app = Application()
app.mainloop()

# a = Project_Log()
# a.add_project("4765", 42995, "Salk", "RRBS")
# projects = a.get_by_status("TO DO")
# print(projects)
