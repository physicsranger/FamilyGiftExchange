import tkinter as tki
from tkinter import ttk

import os,sqlite3,glob
from functools import reduce

from GiftExchangeUtilities.create import create_database

from GiftExchangeUtilities.management import add_or_update_family_member,
remove_family_member,query_member

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
		
		self.add_traces()
	
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
		
		self.family=tki.StringVar()
		self.family_label=ttk.Label(parent,text='Choose Family')
		self.family_box=ttk.Combobox(parent,textvariable=self.family)
		self.family_box.bind('<<ComboboxSelected>>',self.get_families)
		self.family_box['value']=self.get_available_families()
		
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
		self.family_member_box.bind('<<ComboboxSelected>>',self.get_member_info)
		
		#significant other variable, label, and combobox
		self.significant_other=tki.StringVar()
		self.significant_other_label=ttk.Label(parent,text='Significant Other')
		self.significant_other_box=ttk.Combobox(parent,
		textvariable=self.significant_other)
		
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
		command=self.add_or_update_member,state='disabled')
		
		self.remove_member_button=ttk.Button(parent,text='Remove Member',
		command=self.remove_member,state='disabled')
		
		self.quit_button=ttk.Button(parent,text='Quit',command=self.master.destroy)
	
	def grid_all(self):
		self.grid_create_frame()
		
		self.grid_family_frame()
	
	def grid_create_frame(self):
		#first, place the frame itself at top, tell it to fill horizontally
		self.create_frame.grid(column=0,row=0,sticky='NESW')
		
		#now, place the widgets within the frame
		self.create_button.grid(column=0,row=0,sticky='E')
		
		self.family_label.grid(column=1,row=0)
		self.family_box.grid(column=2,row=0,sticky='W')
		
		self.overwrite_check.grid(column=3,row=0,sticky='E')
		self.overwrite_label.grid(column=4,row=0)
	
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
	
	#function to add traces to variables
	#currently it is a bit odd to add traces to the frames separately
	#but leave it like this in case we decide more need to be added
	def add_traces(self):
		self.add_create_traces()
		self.add_family_traces()
	
	def add_create_traces(self):
		self.family.trace_add('write',self.list_family)
	
	def add_family_traces(self):
		self.family_member.trace_add('write',self.get_member_info)


####class utility functions
	def create_family(self,*args):
		#create the empty database file
		if self.family=='':
			self.prompt_for_family()
		
		if self.family=='':
			print('No family choice made, will not create database.')
			return
		else:
			#the trace on the family variable should mean we automatically
			#make this when we update the value, but we'll check just in case
			if not hasattr(self,'database_directory'):
				self.database_directory=os.path.join(self.app.app_dir,
				'GiftExchange_data',f'data_family_{self.family.get()}')
				
				self.database_file=os.path.join(self.database_directory,
				"GiftExchange.db")
			
			#check to make sure that the GiftExchange_data directory exists
			#since this is in the .gitignore file
			#try and make it if not
			if not os.path.exists(os.path.dirname(self.database_directory)):
				try:
					os.mkdir(os.path.dirname(self.database_directory))
				except:
					print(f'Directory for family data does not exist, but could not make directory:\n{os.path.dirname(self.database_directory)}\nCannot create database.')
					return
			
			#check to see if the directory for this specific family exists
			#if not, try and make it
			if not os.path.exists(self.database_directory):
				try:
					os.mkdir(self.database_directory)
				except:
					print(f'Data directory for family {self.family.get()} does not exist, but could not make directory:\n{self.database_directory.get()}.\nCannot create database.')
					return
			
			#may add a try except statement here later, but for now
			#we'll want to capture any potential output
			create_database(self.database_file,self.overwrite.get())
		return
	
	#function to get family name if not specified
	def prompt_for_family(self,*args):
		prompt_window=tki.Toplevel(self.master)
		window_frame=ttk.Frame(prompt_window,borderwidth=2,relief='raised')
		main_label=ttk.Label(window_frame,text='Choose Family To Create Database For')
		family_choice=ttk.StringVar()
		
		window_frame.grid(column=0,row=0)
		main_label.grid(column=0,row=0,columnspan=2)
		
		#def an ad hoc function for a button in the new window
		def assign_and_quit(*args):
			self.family.set(family_choice.get())
			prompt_window.destroy()
		
		#def an ad hoc function to enable choice button
		def check_family(*args):
			if family_choice.get()=='':
				choice_button['state']='disabeled'
			else:
				choice_button['state']='normal'
		
		families=self.get_available_families()
		
		if families:
			check_buttons=[ttk.Radiobutton(window_frame,text=family,variable=family_choice,value=family) for family in families]
			for idx,check in enumerate(check_buttons):
				check.grid(column=0,row=1+idx,columnspan=2,sticky='W')
		
		new_label=ttk.Label(window_frame,text='Add New Family')
		new_entry=ttk.Entry(window_frame,textvariable=family_choice)
		
		new_label.grid(column=0,row=1+len(families))
		new_label.grid(column=0,row=1+len(families))
		
		choice_button=ttk.Button(window_frame,text='Choose Family',
		command=assign_and_quit,state='disabeled')
		
		choice_button.grid(column=0,row=2+len(families),columnspan=2)
		
		family_choice.trace_add('write',check_family)	
		
		prompt_window.grab_set()
		
		return
	
	#function to list which families are available by investigating
	def get_available_families(self,*args):
		#check for available families
		families=[]
		if os.path.exists(os.path.join(self.app.app_directory,'GiftExchange_data')):
			dir_list=glob.glob(os.path.join(self.app.app_directory,
			'GiftExchange_data','data_family_*'))
			if dir_list:
				#we want to split on the underscore
				#but allow for underscores in family names
				families=[reduce(lambda:s1,s2:s1+'_'+s2,dir_name.split('_')[2:]) for dir_name in dir_list]
		
		return families
	
	#function to insert a new member into the family or alter the info
	#of an existing member
	def add_or_update_member(self,*args):
		#simply a way to call the utility function from the button
		add_or_update_family_member(self.database_file,self.make_member_dictionary())
	
	#function to make a member dictionary needed for some utility functions
	def make_member_dictionary(self,*args):
		member={'family':{'name':self.family_member.get(),
		'email':self.email.get(),
		'address':reduce(lambda s1,s2:s1.get()+'\n'+s2.get(),[self.address_line_1,
		self.address_line_2,self.city,self.state,self.zip_code,self.country])},
		'significant_other':self.significant_other.get()}
		return member
	
	#function to remove a family member from the database
	def remove_member(self,*args):
		#simply a way to call the utility function from the button
		remove_family_member(self.database_file,self.family_member.get())
		
		#after that, update the family member list
		self.list_family()
	
	#function to get the list of family member names from the data base and populate
	#the combo boxes
	def list_family(self,*args):
		if self.family!='':
			self.database_directory=os.path.join(self.app.app_dir,
			'GiftExchange_data',f'data_family_{self.family.get()}')
			self.database_file.os.path.join(self.database_directory,'GiftExchange.db')
		
			if os.path.exists(self.database_file):
				with sqlite3.connect(dbfile) as con:
					family=con.cursor().execute("SELECT name FROM family").fetchall()
				
				family=[f[0] for f in family]
		
				self.family_member_box['values']=family
				self.significant_other_box['values']=family.append('')
			self.check_family_buttons()
	
	#function to fill in the member info field when the value of the family_member
	#variable is changed
	def get_member_info(self,*args):
		#get the info from the database if family member has been specified
		#if the value has been 'unselected' will check on buttons only
		#will return default values if member is not in the database
		if self.family_member!='':
			member_info=query_member(self.database_file,self.family_member)
			
			#fill in the variables
			self.significant_other.set(member_info['significant_other'])
			self.email.set(member_info['email'])
			
			address=member_info['address'].split('\n')
			self.address_line_1.set(address[0])
			self.address_line_2.set(address[1])
			self.city.set(address[2])
			self.state.set(address[3])
			self.zip_code.set(address[4])
			self.country.set(address[5])
		
		#now check to see if 
		self.check_family_buttons()
	
	#function to monitor the family and family_member values to determine
	#if buttons on the family frame are active or not
	def check_family_buttons(self,*args):
		#if both the family and family_member values are set, the buttons can be
		#active
		if (self.family not in [None,'NULL','']) and (self.family_member not in [None,'NULL','']):
			self.add_or_update_member_button['state']='normal'
			self.remove_member_buton['state']='normal'
		
		#otherwise, disable the buttons
		else:
			self.add_or_update_member_button['state']='disabled'
			self.remove_member_buton['state']='disabled'
		
		
