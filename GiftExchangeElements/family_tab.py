import tkinter as tki
from tkinter import ttk

import os,sqlite3,glob,re
from functools import reduce

from GiftExchangeUtilities.create import create_database

from GiftExchangeUtilities.management import (
	add_or_update_family_member,
	remove_family_member,
	query_member)

'''This class creates a tab for the main app notebook where you manage
your family database(s).'''
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
		
		#make the frames within this tab and create widgets for each
		self.make_frames()
		
		#add traces on variables to update other variables and to
		#control button states
		self.add_traces()
	
	#function to make the two frames of the tab and widgets
	#for each
	def make_frames(self):
		#make a frame for the create database button and such
		self.create_frame=ttk.Frame(self,borderwidth=1,relief='sunken')
		self.fill_create_frame(self.create_frame)
		
		#make a frame for managing family info
		self.family_frame=ttk.Frame(self,borderwidth=1,relief='sunken')
		self.fill_family_frame(self.family_frame)
	
	#create the widgets which will go in the create frame
	def fill_create_frame(self,parent):
		#make a button to create an empty database with
		#all the tables we'll want to fill in later
		self.create_button=ttk.Button(parent,text='Create Family',
		    command=self.create_family,state='disabled',style='Off.TButton')
		
		#need a variable for the family we're working with, also create
		#a drop down box listing possible families
		self.family=tki.StringVar()
		self.family_label=ttk.Label(parent,text='Choose Family')
		self.family_box=ttk.Combobox(parent,textvariable=self.family)
		self.family_box.bind('<<ComboboxSelected>>',self.get_available_families)
		self.family_box['values']=self.get_available_families()
		
		#check button to flag if we want to overwrite an existing
		#database of the same name
		self.overwrite=tki.BooleanVar(value=False)
		self.overwrite_label=ttk.Label(parent,text='Overwrite')
		self.overwrite_check=ttk.Checkbutton(parent,variable=self.overwrite,
		    onvalue=True,offvalue=False)
	
	#function to create widgets within the family frame
	#given the desired setup, we make Frames for the individual rows
	#and then call a function to make widgets for each row	
	def fill_family_frame(self,parent):
		#make the first row with family member and significant other
		#labels and dropdown boxes
		self.first_family_row=ttk.Frame(parent,borderwidth=1,relief='flat')
		self.fill_first_family_row(self.first_family_row)
		
		#make the second row for the email address
		self.second_family_row=ttk.Frame(parent,borderwidth=1,relief='flat')
		self.fill_second_family_row(self.second_family_row)
		
		#make the third row for address line 1
		self.third_family_row=ttk.Frame(parent,borderwidth=1,relief='flat')
		self.fill_third_family_row(self.third_family_row)
		
		#make the fourth row for address line 2
		self.fourth_family_row=ttk.Frame(parent,borderwidth=1,relief='flat')
		self.fill_fourth_family_row(self.fourth_family_row)
		
		#make the fifth row for city, state, and zip
		self.fifth_family_row=ttk.Frame(parent,borderwidth=1,relief='flat')
		self.fill_fifth_family_row(self.fifth_family_row)
		
		#make the sixth row for country
		self.sixth_family_row=ttk.Frame(parent,borderwidth=1,relief='flat')
		self.fill_sixth_family_row(self.sixth_family_row)
		
		#make the seventh row for buttons
		self.seventh_family_row=ttk.Frame(parent,borderwidth=1,relief='flat')
		self.fill_seventh_family_row(self.seventh_family_row)
	
	#function to create widgets for the first row of the family frame
	def fill_first_family_row(self,parent):
		#variable, label, and combobox entry for a family member
		self.family_member=tki.StringVar()
		self.family_member_label=ttk.Label(parent,text='Family Member:')
		self.family_member_box=ttk.Combobox(parent,textvariable=self.family_member)
		self.family_member_box.bind('<<ComboboxSelected>>',self.list_family)
		
		#significant other variable, label, and combobox
		self.significant_other=tki.StringVar()
		self.significant_other_label=ttk.Label(parent,text='Significant Other:')
		self.significant_other_box=ttk.Combobox(parent,
		    textvariable=self.significant_other)
		self.significant_other_box.bind('<<ComboboxSelected>>',self.list_family)
	
	#function to create widgets for the second row of the family frame
	def fill_second_family_row(self,parent):
		#now create variables and widgets for the family member
		#email and address info
		self.email=tki.StringVar()
		self.email_label=ttk.Label(parent,text='Email address:')
		self.email_entry=ttk.Entry(parent,textvariable=self.email)#,width=30)
	
	#function to create widgets for the third row of the family frame
	def fill_third_family_row(self,parent):
		self.address_line_1=tki.StringVar()
		self.address_line_1_label=ttk.Label(parent,text='Address line 1')
		self.address_line_1_entry=ttk.Entry(parent,
		    textvariable=self.address_line_1)#,width=40)
	
	#function to create widgets for the fourth row of the family frame
	def fill_fourth_family_row(self,parent):
		self.address_line_2=tki.StringVar()
		self.address_line_2_label=ttk.Label(parent,text='Address line 2')
		self.address_line_2_entry=ttk.Entry(parent,
		    textvariable=self.address_line_2)#,width=40)
	
	#function to create widgets for the fith row of the family frame
	def fill_fifth_family_row(self,parent):
		self.city=tki.StringVar()
		self.state=tki.StringVar()
		self.zip_code=tki.StringVar()
		
		self.city_label=ttk.Label(parent,text='City')
		self.state_label=ttk.Label(parent,text='State/Province')
		self.zip_code_label=ttk.Label(parent,text='Zip code')
		
		self.city_entry=ttk.Entry(parent,textvariable=self.city,width=12)
		self.state_entry=ttk.Entry(parent,textvariable=self.state,width=12)
		self.zip_code_entry=ttk.Entry(parent,textvariable=self.zip_code,width=8)
	
	#function to create widgets for the sixth row of the family frame
	def fill_sixth_family_row(self,parent):
		self.country=tki.StringVar()
		self.country_label=ttk.Label(parent,text='Country')
		self.country_entry=ttk.Entry(parent,textvariable=self.country,width=12)
	
	#function to create widgets for the seventh row of the family frame
	def fill_seventh_family_row(self,parent):
		self.add_or_update_member_button=ttk.Button(parent,text='Add/Update Member Info',
		    command=self.add_or_update_member,state='disabled',style='Off.TButton')
		
		self.remove_member_button=ttk.Button(parent,text='Remove Member',
		    command=self.remove_member,state='disabled',style='Off.TButton')
		
		self.quit_button=ttk.Button(parent,text='Quit',command=self.quit)
	
	#function to call pack all widgets associated with this tab
	def pack_all(self):
		#first, pack everything in the create frame
		self.pack_create_frame()
		
		#next, pack everything in the family frame
		self.pack_family_frame()
	
	#pack the create frame and widgets within the frame
	def pack_create_frame(self):
		#first, place the frame itself at top, tell it to fill horizontally
		self.create_frame.pack(side='top',fill='x',expand=True)
		
		#now, place the widgets within the frame
		self.create_button.pack(side='left')
		
		self.family_label.pack(side='left',padx=(8,0))
		self.family_box.pack(side='left',padx=(0,8))
		
		self.overwrite_check.pack(side='left')
		self.overwrite_label.pack(side='left')
	
	#function to pack the family frame and then, one row at at time
	#pack the rest of the widgets
	def pack_family_frame(self):
		#first,place the frame itself, below create frame, set to fill horizontally
		self.family_frame.pack(side='top',fill='both',expand=True)
		
		#now pack the rows
		self.pack_first_family_row()
		
		self.pack_second_family_row()
		
		self.pack_third_family_row()
		
		self.pack_fourth_family_row()
		
		self.pack_fifth_family_row()
		
		self.pack_sixth_family_row()
		
		self.pack_seventh_family_row()
	
	#pack the first row of the family frame and widgets within it	
	def pack_first_family_row(self):
		self.first_family_row.pack(side='top',fill='x')
		
		self.family_member_label.pack(side='left')
		self.family_member_box.pack(side='left',padx=(0,8))
		
		self.significant_other_label.pack(side='left')
		self.significant_other_box.pack(side='left')
	
	#pack the second row of the family frame and widgets within it
	def pack_second_family_row(self):
		self.second_family_row.pack(side='top',fill='x')
		
		self.email_label.pack(side='left')
		self.email_entry.pack(side='left',fill='x',expand=True,padx=(0,8))
	
	#pack the third row of the family frame and widgets within it	
	def pack_third_family_row(self):
		self.third_family_row.pack(side='top',fill='x')
		
		self.address_line_1_label.pack(side='left')
		self.address_line_1_entry.pack(side='left',fill='x',expand=True,padx=(0,8))
	
	#pack the fourth row of the family frame and widgets within it
	def pack_fourth_family_row(self):
		self.fourth_family_row.pack(side='top',fill='x')
		
		self.address_line_2_label.pack(side='left')
		self.address_line_2_entry.pack(side='left',fill='x',expand=True,padx=(0,8))
	
	#pack the fifth row of the family frame and widgets within it
	def pack_fifth_family_row(self):
		self.fifth_family_row.pack(side='top',fill='x')
		
		self.city_label.pack(side='left')
		self.city_entry.pack(side='left',padx=(0,8))
		
		self.state_label.pack(side='left')
		self.state_entry.pack(side='left',padx=(0,8))
		
		self.zip_code_label.pack(side='left')
		self.zip_code_entry.pack(side='left')
	
	#pack the sixth row of the family frame and widgets within it
	def pack_sixth_family_row(self):
		self.sixth_family_row.pack(side='top',fill='x')
		
		self.country_label.pack(side='left')
		self.country_entry.pack(side='left')
	
	#pack the seventh row of the family frame and widgets within it	
	def pack_seventh_family_row(self):
		self.seventh_family_row.pack(side='top',fill='x')
		
		self.add_or_update_member_button.pack(side='left',padx=(0,8))
		self.remove_member_button.pack(side='left',padx=(8,8))
		self.quit_button.pack(side='left',padx=(8,0))
	
	#function to add traces to variables
	def add_traces(self):
		#add traces for the create frame
		self.add_create_traces()
		
		#add traces for the family frame
		self.add_family_traces()
	
	#traces on variables associated with the create frame
	def add_create_traces(self):
		#we want to know if the family value is updated to update list of
		#members and to activate or not the create button
		#use the same trace on overwrite to change button state
		self.family.trace_add('write',self.list_family)
		self.overwrite.trace_add('write',self.check_family_buttons)
	
	#traces on variables associated with the family frame
	def add_family_traces(self):
		#if the family member info changes, fill in info if they are
		#already in the database
		self.family_member.trace_add('write',self.get_member_info)

####class utility functions
	#function to create an empty database for a family
	def create_family(self,*args):
		#create the empty database file
		print(f'Beginning creation of database for family {self.family.get()}, any whitespaces will be replaced with underscores.')
		
		#at this point, replace white spaces with underscores
		for token in re.findall('[\s]+',self.family.get()):
			self.family.set(self.family.get().replace(token,'_'))
		
		#to pretty things up in the case of multiple spaces or tabs in sequence
		#we'll reduce things down to at most one subsequent underscore
		while '__' in self.family.get():
			self.family.set(self.family.get().replace('__','_'))
		
		#the trace on the family variable should mean we automatically
		#make this when we update the value, but we'll check just in case
		if not hasattr(self,'database_directory'):
			self.database_directory=os.path.join(self.app.app_directory,
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
		
		#open up a prompt window to make sure the user really wants to overwrite the file
		if self.family.get() in self.get_available_families()\
		    and self.overwrite.get():
		    self.prompt_for_overwrite()
		else:
			self.proceed=True
		
		#if we've got the go ahead, make the database
		if self.proceed:
			create_database(self.database_file,self.overwrite.get())
		else:
			print(f'Okay, we will not overwrite database for family {self.family.get()}.')
		
		del self.proceed
		
	
	#function to list which families are available by investigating the
	#subdirectories of the GiftExchange_data directory
	def get_available_families(self,*args):
		#check for available families
		families=[]
		if os.path.exists(os.path.join(self.app.app_directory,'GiftExchange_data')):
			dir_list=glob.glob(os.path.join(self.app.app_directory,
			'GiftExchange_data','data_family_*'))
			if dir_list:
				#we want to split on the underscore
				#but allow for underscores in family names
				families=[reduce(lambda s1,s2:s1+'_'+s2,\
				    dir_name.split(os.sep)[-1].split('_')[2:])\
				    for dir_name in dir_list]
		
		#now that we know which families are available, add them
		#to the family_box
		self.family_box['values']=families
		
		return families
	
	#function to insert a new member into the family or alter the info
	#of an existing member
	def add_or_update_member(self,*args):
		#simply a way to call the utility function from the button
		add_or_update_family_member(self.database_file,self.make_member_dictionary())
	
	#function to make a member dictionary, needed for some utility functions
	def make_member_dictionary(self,*args):
		member={'family':{'name':self.family_member.get(),
		  'email':self.email.get()}}
		
		address=reduce(lambda s1,s2:s1+'\n'+s2,[self.address_line_1.get(),
		    self.address_line_2.get(),self.city.get(),self.state.get(),
		    self.zip_code.get(),self.country.get()])
		if address!='\n\n\n\n\n':
			member['family']['address']=address
			
		if self.significant_other.get()!='':
			member['significant_other']=self.significant_other.get()
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
		if self.family.get()!='':
			self.database_directory=os.path.join(self.app.app_directory,
			    'GiftExchange_data',f'data_family_{self.family.get()}')
			self.database_file=os.path.join(self.database_directory,'GiftExchange.db')
		
			if os.path.exists(self.database_file):
				con=sqlite3.connect(self.database_file)
				family_members=con.cursor().execute('''SELECT name 
				    FROM family''').fetchall()
				if family_members is None:
					family_members=[]
				else:
					family_members=[f[0] for f in family_members]
		
				self.family_member_box['values']=family_members
				self.significant_other_box['values']=family_members+['']
			self.check_family_buttons()
	
	#function to fill in the member info field when the value of the family_member
	#variable is changed
	def get_member_info(self,*args):
		#get the info from the database if family member has been specified
		#if the value has been 'unselected' will check on buttons only
		#will return default values if member is not in the database
		if self.family_member.get() in self.family_member_box['values']:
			member_info=query_member(self.database_file,self.family_member.get())
			
			#fill in the variables
			self.significant_other.set(member_info.get('significant_other'))
			self.email.set('' if member_info['email'] is None\
			    else member_info['email'])
			
			address=member_info['address']
			if address is not None:
				address=address.split('\n')
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
		create_state=('normal' if (self.family.get()\
		 not in [None,'NULL','']+self.get_available_families()) or\
		 (self.family.get() in self.get_available_families()\
		  and self.overwrite.get()) else 'disabled')
	
		create_style=('On.TButton' if create_state=='normal' else 'Off.TButton')
	
		self.create_button['state']=create_state
		self.create_button['style']=create_style
		
		member_state=('normal' if (self.family.get() not in [None,'NULL','']) and \
		    (self.family_member.get() not in [None,'NULL','']) else 'disabled')
	
		member_style=('On.TButton' if member_state=='normal' else 'Off.TButton')
		 
		self.add_or_update_member_button['state']=member_state
		self.remove_member_button['state']=member_state
		
		self.add_or_update_member_button['style']=member_style
		self.remove_member_button['style']=member_style
	
	#create a new window to create a second chance prompt when the overwrite checkbutton
	#is checked and the user is attempting to create a database for a family
	#which already exists
	def prompt_for_overwrite(self,*args):
		#def functions for the proceed or don't proceed buttons
		def go_ahead(*args):
			self.proceed=True
			overwrite_prompt.grab_release()
			overwrite_prompt.after(10,overwrite_prompt.destroy)
		
		def no_go(*args):
			self.proceed=False
			overwrite_prompt.grab_release()
			overwrite_prompt.after(10,overwrite_prompt.destroy)
		
		#create a new toplevel window
		overwrite_prompt=tki.Toplevel(self.master)
		overwrite_prompt.title('Second Chance')
		
		#use a label to display the prompt message
		overwrite_label=ttk.Label(overwrite_prompt,text=f'Database exists for family "{self.family.get()}".\n\nOvewrite box is checked.\n\nDo you wish to proceed with creating\na new database for this family?')
		
		#make buttons for yes and no
		overwrite_yes=ttk.Button(overwrite_prompt,text='Yes',style='On.TButton',
		    command=go_ahead)
		
		overwrite_no=ttk.Button(overwrite_prompt,text='No',style='On.TButton',
		    command=no_go)
		
		#grid everything
		overwrite_label.grid(column=0,row=0,columnspan=2,sticky='NESW',
		    pady=(4,12),padx=4)
		
		overwrite_yes.grid(column=0,row=1)
		overwrite_no.grid(column=1,row=1)
		
		#grab_set and make sure that nothing else happens
		#while this window exists
		overwrite_prompt.grab_set()
		overwrite_prompt.wait_window()
		
	
	#function for quit button, I think using the 'after' method will avoid
	#the GUI hanging up as I'm seeing on my mac
	def quit(self,*args):
		self.master.after(10,self.master.destroy)
