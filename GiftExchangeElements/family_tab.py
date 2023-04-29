import tkinter as tki
from tkinter import ttk,filedialog
import os,sqlite3
from gift_exchange_utilities import create_database

#make a class for the main tab where you manage your family database
#and create the gift draws for a given year
class FamilyTab(ttk.Frame):
	def __init__(self,parent,app,master,*args,**kwargs):
		#do the Frame initialization
		ttk.Frame.__init__(self)
		
		#assign some attributes so we can access the notebook, app, and Tk instance
		self.parent=parent
		self.app=app
		self.master=master
		
		#add this tab to the notebook
		self.parent.add(self,*args,**kwargs)
		
		self.make_frames()
	
	def make_frames(self):
		#make a frame for the create database button and such
		self.create_frame=ttk.Frame(self,borderwidth=1,relief='sunken')
		self.fill_create_frame(self.create_frame)
		
		#make a frame for entering family info
		self.family_frame=ttk.Frame(self,borderwidth=1,relief='sunken')
		self.fill_family_frame(self.family_frame)
	
	def fill_create_frame(self,parent):
		#first off, button to create an empty database with
		#all the tables we'll want to fill in later
		self.create_button=ttk.Button(parent,text='Create Family',
		command=self.create_family)
		
		#button to get the directory to save the database in and to
		#know where to look for it...this may be hardcoded later,
		#start with current working directory
		self.database_directory=tki.StringVar(value=os.getcwd())
		self.database_directory_button=ttk.Button(parent,
		text=f'Save Location',command=self.update_database_directory)
		
		#set a default name, allow for it to be changed
		self.database_file_name=tki.StringVar(value='FamilyGiftExchange.db')
		self.database_file_name_label=ttk.Label(parent,text='Database Name')
		self.database_file_name_entry=ttk.Entry(parent,
		textvariable=self.database_file_name,width=20)
		
		#check button to flag if we want to overwrite an existing
		#database of the same name
		self.overwrite=tki.BooleanVar(value=False)
		self.overwrite_label=ttk.Label(parent,text='Overwrite')
		self.overwrite_check=ttk.Checkbutton(parent,variable=self.overwrite,
		onvalue=True,offvalue=False)
		
	def fill_family_frame(self,parent):
		#variable, label, and combobox entry for a family member
		self.family_member=tki.StringVar()
		self.family_member_label=ttk.Label(parent,text='Family Member')
		self.family_member_box=ttk.Combobox(parent,textvariable=self.family_member)
		self.family_member_box.bind('<<ComboboxSelected>>',self.list_family)
		
		#significant other variable, label, and combobox
		self.significant_other=tki.StringVar()
		self.significant_other_label=ttk.Label(parent,text='Significant Other')
		self.significant_other_box=ttk.Combobox(parent,
		textvariable=self.significant_other)
		
		#populate the values for the Combobox, if the database already exists
		self.list_family()
		
		#now create variables and widgets for the family member
		#email and address info
		self.email=tki.StringVar()
		self.email_label=ttk.Label(parent,text='Email address')
		self.email_entry=ttk.Entry(parent,textvariable=self.email,width=30)
		
		self.address_line_1=tki.StringVar()
		self.address_line_2=tki.StringVar()
		self.city=tki.StringVar()
		self.state=tki.StringVar()
		self.zip_code=tki.StringVar()
		self.country=tki.StringVar()
		
		self.address_line_1_label=ttk.Label(parent,text='Address line 1')
		self.address_line_2_label=ttk.Label(parent,text='Address line 2')
		self.city_label=ttk.Label(parent,text='City')
		self.state_label=ttk.Label(parent,text='State/Province')
		self.zip_code_label=ttk.Label(parent,text='Zip code')
		self.country_label=ttk.Label(parent,text='Country')
		
		self.address_line_1_entry=ttk.Entry(parent,
		textvariable=self.address_line_1,width=40)
		
		self.address_line_2_entry=ttk.Entry(parent,
		textvariable=self.address_line_2,width=40)
		
		self.city_entry=ttk.Entry(parent,textvariable=self.city,width=12)
		self.state_entry=ttk.Entry(parent,textvariable=self.state,width=12)
		self.zip_code_entry=ttk.Entry(parent,textvariable=self.zip_code,width=8)
		self.country_entry=ttk.Entry(parent,textvariable=self.country,width=12)
		
		#add a couple of buttons
		self.add_or_update_member_button=ttk.Button(parent,text='Add/Update Member Info',
		command=self.add_or_update_member)
		
		self.remove_member_button=ttk.Button(parent,text='Remove Member',
		command=self.remove_member)
		
		self.quit_button=ttk.Button(parent,text='Quit',command=self.master.destroy)
	
	def grid_all(self):
		self.grid_create_frame()
		
		self.grid_family_frame()
	
	def grid_create_frame(self):
		#first, place the frame itself at top, tell it to fill horizontally
		self.create_frame.grid(column=0,row=0,sticky='NESW')
		
		#now, place the widgets within the frame
		self.create_button.grid(column=0,row=0,sticky='E')
		self.database_directory_button.grid(column=1,row=0)
		self.database_file_name_label.grid(column=2,row=0)
		self.database_file_name_entry.grid(column=3,row=0,columnspan=2,sticky='W')
		
		self.overwrite_check.grid(column=5,row=0,sticky='E')
		self.overwrite_label.grid(column=6,row=0)
	
	def grid_family_frame(self):
		#first,place the frame itself, below create frame, set to fill horizontally
		self.family_frame.grid(column=0,row=1,sticky='NESW')		
		#now place widgets within the frame
		self.family_member_label.grid(column=0,row=0)
		self.family_member_box.grid(column=1,row=0,columnspan=2,sticky='W')
		
		self.significant_other_label.grid(column=3,row=0)
		self.significant_other_box.grid(column=4,row=0,columnspan=2,sticky='W')
		
		self.email_label.grid(column=0,row=1)
		self.email_entry.grid(column=1,row=1,columnspan=3,sticky='W')
		
		self.address_line_1_label.grid(column=0,row=2)
		self.address_line_1_entry.grid(column=1,row=2,columnspan=4,sticky='W')
		self.address_line_2_label.grid(column=0,row=3)
		self.address_line_2_entry.grid(column=1,row=3,columnspan=4,sticky='W')
		
		self.city_label.grid(column=0,row=4)
		self.city_entry.grid(column=1,row=4,sticky='W')
		self.state_label.grid(column=2,row=4)
		self.state_entry.grid(column=3,row=4,sticky='W')
		self.zip_code_label.grid(column=4,row=4)
		self.zip_code_entry.grid(column=5,row=4,sticky='W')
		
		self.country_label.grid(column=0,row=5)
		self.country_entry.grid(column=1,row=5,sticky='W')
		
		self.add_or_update_member_button.grid(column=0,row=6,columnspan=2,sticky='W')
		self.remove_member_button.grid(column=2,row=6,columnspan=2,sticky='W')
		self.quit_button.grid(column=4,row=6)
	
	def create_family(self):
		#create the empty database file
		##create_database(database_file=os.path.join(self.database_directory.get(),
		##self.database_file_name.get()),overwrite=self.overwrite.get())
		
		#need some way to let the user know that the creation was successful
		#perhaps use the terminal window widget from my SUPERB GUI
		#will need that since create_database has print statements
		
		return
	
	def update_database_directory(self):
		#use the filedialog stuff to select a new save directory
		#see if there is someway to make a default directory
		#within the repo such that the database itself is excluded
		return
	
	def add_or_update_member(self):
		#code to insert a new member or alter their info in a particular table
		
		#after that, update the family member list
		self.list_family()
	
	def remove_member(self):
		#code to remove someone from the database
		
		#after that, update the family member list
		self.list_family()
	
	def list_family(self,*args):
		#get the list of family member names from the data base and populate
		#the combo boxes
		dbfile=os.path.join(self.database_directory.get(),
		self.database_file_name.get())
		
		if os.path.exists(dbfile):
			with sqlite3.connect(dbfile) as con:
				family=con.cursor().execute("SELECT name FROM family").fetchall()
		
			self.family_member_box['values']=family
			self.significant_other_box['values']=family
		
		
