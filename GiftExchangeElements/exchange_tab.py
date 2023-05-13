import tkinter as tki
from tkinter import ttk
import time,os,glob
import pandas as pd

from rich import print as rprint
from rich.table import Table

from functools import reduce

from GiftExchangeUtilities.name_draw import (
    generate_exchange,
    output_giftee_assignments,
    get_previous_years,
    valid_year,
    add_previous_year,
    get_num_previous_years)

'''This class creates a tab for the main app notebook where you manage
the actual gift exchange(s).'''
class ExchangeTab(ttk.Frame):
	def __init__(self,parent,app,master,*args,**kwargs):
		#do the frame initialization
		ttk.Frame.__init__(self)
		
		#assign some attributes so we can access the notebook, app, and Tk instance
		self.parent=parent
		self.app=app
		self.master=master
		
		#instead of redefining the same function
		#point to the family tab, may cause issues
		#if someone tried to use this split off from the main code
		self.get_available_families=self.app.family_tab.get_available_families
		
		#add this tab to the notebook
		self.parent.add(self,*args,**kwargs)
		
		#make the frame and associated widgets for this tab
		self.make_frames()
		
		#add traces on variables
		self.add_traces()
	
	#function to make the frame for this tab and then
	#make sub frames to represent rows for the layout we want 
	def make_frames(self):
		self.exchange_frame=ttk.Frame(self,borderwidth=1,relief='sunken')
		
		#make a frame for the first row and create widgets for it
		self.first_row=ttk.Frame(self.exchange_frame,borderwidth=1,relief='flat')
		self.fill_first_row(self.first_row)
		
		#make a frame for the second row and create widgets for it
		self.second_row=ttk.Frame(self.exchange_frame,borderwidth=1,relief='flat')
		self.fill_second_row(self.second_row)
		
		#make a frame for the third row and create widgets for it
		self.third_row=ttk.Frame(self.exchange_frame,borderwidth=1,relief='flat')
		self.fill_third_row(self.third_row)
		
		#make a frame for the fourth row and create widgets for it
		self.fourth_row=ttk.Frame(self.exchange_frame,borderwidth=1,relief='flat')
		self.fill_fourth_row(self.fourth_row)
		
		#make a frame for the fifth row and create widgets for it
		self.fifth_row=ttk.Frame(self.exchange_frame,borderwidth=1,relief='flat')
		self.fill_fifth_row(self.fifth_row)
	
	#create widgets within the first row
	def fill_first_row(self,parent):
		#button to draw names, start out disabled by default, put a trace
		#on the family variable (can we have multiple traces at once?)
		self.draw_names_button=ttk.Button(parent,text='Draw Names',
		    command=self.draw_names,state='disabled',style='Off.TButton')
		    
		#we expect that this should be called after the family frame
		#so we can make it point to the same family variable
		if hasattr(self.app,'family_tab'):
			self.family=self.app.family_tab.family
		else:
			self.family=tki.StringVar()
		
		#create a similar family drop down box
		self.family_label=ttk.Label(parent,text='Family:',
		padding=(2,1,1,1))
		self.family_box=ttk.Combobox(parent,textvariable=self.family,
		    width=14)
		self.family_box.bind('<<ComboboxSelected>>',self.get_available_families)
		self.family_box['values']=self.get_available_families()
		
		#create spin box to select how many previous years to use
		#when determining gifter giftee excludes
		self.exclude_num_previous=tki.IntVar(value=1)
		self.exclude_num_previous_label=ttk.Label(parent,
		    text='Number of previous years to exclude giftees',
		    padding=(2,1,1,1))
		self.exclude_num_previous_spinbox=ttk.Spinbox(parent,
		    from_=0,to=max(1,self.get_num_years()),increment=1,width=2,
		    textvariable=self.exclude_num_previous)
	
	#create widgets within the second row
	def fill_second_row(self,parent):
		#Default to the current year
		self.exchange_year=tki.StringVar(value=time.localtime().tm_year)
		self.exchange_year_label=ttk.Label(parent,text='Year:',width=4)
		self.exchange_year_entry=ttk.Entry(parent,
		    textvariable=self.exchange_year,width=4)
		
		#Allow that people may need to redo a name draw for a given year
		self.overwrite_year=tki.BooleanVar(value=False)
		self.overwrite_year_check=ttk.Checkbutton(parent,
		    variable=self.overwrite_year,onvalue=True,offvalue=False)
		self.overwrite_year_label=ttk.Label(parent,
		    text='Replace existing year?')
		
		#allow that some members may not participate every year
		self.skip_members=[]
		self.skip_members_button=ttk.Button(parent,
		    text='Choose members to skip',command=self.choose_members_to_skip,
		    state='disabled',style='Off.TButton')	
	
	#create widgets for the third row
	def fill_third_row(self,parent):
		#This row focuses on viewing gifter-giftee assignments
		#for previous years, though the current year can be shown
		self.view_previous_years_button=ttk.Button(parent,
		    text='View Previous Years',command=self.view_previous,state='disabled',
		    style='Off.TButton')
		
		self.num_previous=tki.IntVar(value=1)
		self.num_previous_label=ttk.Label(parent,text='Number of years to view')
		self.num_previous_entry=ttk.Entry(parent,
		    textvariable=self.num_previous,width=2)
		
		self.include_current=tki.BooleanVar(value=False)
		self.include_current_check=ttk.Checkbutton(parent,
		    variable=self.include_current,onvalue=True,offvalue=False)
		self.include_current_label=ttk.Label(parent,text='Including Current?')
	
	#create widgets for the fourth row
	def fill_fourth_row(self,parent):
		#allow name draw info from previous years to be input directly
		self.input_previous_year_button=ttk.Button(parent,
		   text='Input Data For Previous Year',command=self.input_previous,
		   state='disabled',style='Off.TButton')
	
	#create a quit button for the fifth row
	def fill_fifth_row(self,parent):
		self.quit_button=ttk.Button(parent,text='Quit',command=self.quit)
	
	#pack the frame, each row, and all widgets in the rows.
	def pack_all(self):
		#pack the frame itself
		self.exchange_frame.pack(expand=True,fill='both')
		
		#now pack the rows in order
		self.pack_first_row()
		self.pack_second_row()
		self.pack_third_row()
		self.pack_fourth_row()
		self.pack_fifth_row()
	
	#function to pack the first row and widgets within it
	def pack_first_row(self):
		self.first_row.pack(side='top',fill='x')
		self.draw_names_button.pack(side='left')
		self.family_label.pack(side='left',padx=(8,0))
		self.family_box.pack(side='left',padx=(0,8))
		self.exclude_num_previous_label.pack(side='left')
		#self.exclude_num_previous_entry.pack(side='left')
		self.exclude_num_previous_spinbox.pack(side='left')
	
	#function to pack the second row and widgets within it
	def pack_second_row(self):
		self.second_row.pack(side='top',fill='x')
		self.exchange_year_label.pack(side='left')
		self.exchange_year_entry.pack(side='left')
		self.overwrite_year_label.pack(side='left',padx=(8,0))
		self.overwrite_year_check.pack(side='left',padx=(0,8))
		self.skip_members_button.pack(side='left')
	
	#function to pack the third row and widgets within it
	def pack_third_row(self):
		self.third_row.pack(side='top',fill='x',pady=(8,8))
		self.view_previous_years_button.pack(side='left')
		self.num_previous_label.pack(side='left',padx=(8,0))
		self.num_previous_entry.pack(side='left',padx=(0,8))
		self.include_current_label.pack(side='left')
		self.include_current_check.pack(side='left')
	
	#function to pack the fourth row and widgets within it
	def pack_fourth_row(self):
		self.fourth_row.pack(side='top',fill='x',pady=(8,8))
		self.input_previous_year_button.pack(side='left')
	
	#function to pack the fifth row and widgets within it
	def pack_fifth_row(self):
		self.fifth_row.pack(side='top',fill='x',pady=(8,8))
		self.quit_button.pack(side='left')
	
	#function to add traces on variables
	#even though we only have one frame, keep the approach (calling another method)
	#in case we add more in the future
	def add_traces(self,*args):
		self.add_exchange_traces()
	
	#add traces on variables associated with the exchange_frame
	def add_exchange_traces(self,*args):
		#need to make sure the family selection is valid
		#before activating the buttons
		self.family.trace_add('write',self.check_exchange_buttons)
	
	#function to do the name draw
	def draw_names(self,*args):
		#make sure we have the database file
		if hasattr(self.app.family_tab,'database_file'):
			database_file=self.app.family_tab.database_file
		else:
			database_directory=os.path.join(self.app.app_directory,'GiftExchange_data',
			    f'data_family_{self.family.get()}')
				
			database_file=os.path.join(self.database_directory,"GiftExchange.db")
		
		#try to make the name draws	
		success=generate_exchange(database_file,skip_names=self.skip_members,
		    num_previous_exclude=self.exclude_num_previous.get(),
		    overwrite=self.overwrite_year.get(),
		    new_year=self.exchange_year.get())
		
		#if we were able to make the draws, write results out to text files
		#where the file name has the name of the gifter and the content
		#of the file contains the giftee name (and address)
		if success:
			output_giftee_assignments(database_file,self.exchange_year.get())
			print(f'Names drawn and assignments generated text files written in {os.path.join(os.path.dirname(database_file),str(self.exchange_year.get()))}')
		else:
			print('Could not draw names, examine output for error messages.')
		return
	
	#function to designate family members to not be included in a draw for a given year
	#this will be done by creating a bunch of check boxes to select
	def choose_members_to_skip(self,*args):
		#try creating a function dynamically for the button on this window
		def assign_skip_names(*args):
			self.skip_members=[name for name,flag in zip(names,name_flags) if flag.get()]
			skip_window.grab_release()
			skip_window.after(10,skip_window.destroy)
		
		#get the family member names from the family_tab
		names=self.app.family_tab.family_member_box['values']
		
		#if the list of names is not empty
		if names:
			#make a popup window for selecting people to exclude
			skip_window=tki.Toplevel(self.master)
			skip_window.columnconfigure(0,weight=1)
			skip_window.title('Skip Members')
			skip_frame=ttk.Frame(skip_window,borderwidth=1,relief='raised')
			skip_label=ttk.Label(skip_frame,text='Skip?')
			
			#make flags for each name
			name_flags=[tki.BooleanVar(value=False if name not in self.skip_members\
			     else True) for name in names]
			#make checkbuttons for each name
			name_checks=[ttk.Checkbutton(skip_frame,variable=name_flag,
			    onvalue=True,offvalue=False) for name_flag in name_flags]
			#make labels for each name
			name_labels=[ttk.Label(skip_frame,text=name) for name in names]
			
			#make a submit button to process the choices and close the window
			submit_button=ttk.Button(skip_frame,text='Submit',
			    command=assign_skip_names)
			
			#grid everything
			skip_frame.grid(column=0,row=0,sticky='NESW')
			skip_label.grid(column=0,row=0,columnspan=2)
			
			row_idx=1
			for check,label in zip(name_checks,name_labels):
				check.grid(column=0,row=row_idx)
				label.grid(column=1,row=row_idx,sticky='W')
				row_idx+=1
			
			submit_button.grid(column=0,row=row_idx,columnspan=2,
			    padx=10)
			
			skip_window.geometry(f'250x{20*(len(name_checks)+2)+15}')
			
			skip_window.grab_set()
		
		#if names is empty, nothing to do
		else:
			print(f'Name list for family {self.family.get()} came up empty,\
			 nothing to do.')
		
	#function to view exchange draws for previous years by popping out
	#another window
	def view_previous(self,*args):
		if hasattr(self.app.family_tab,'database_file'):
			database_file=self.app.family_tab.database_file
		else:
			database_file=os.path.join(self.app.app_directory,'GiftExchange_data',
			    f'data_family_{self.family.get()}','GiftExchange.db')
		
		#get the information, returned as a nested dictionary
		#where the top level keys are the year values
		#and each nested dictionary has keys of the gifter names with
		#values of the giftee names
		previous_years_draws,names=get_previous_years(database_file,
		    self.num_previous.get(),self.include_current.get())
		
		#straight forward to turn the dictionary and list of names
		#into a dataframe
		previous_exchanges=pd.DataFrame(previous_years_draws,index=names)
		
		#now just display results in the terminal window
		#try to put rich as a dependency, but just in case
		#something goes wrong, try to catch
		try:
			#print(previous_exchanges.to_markdown())
			exchange_table=Table(title='Gift Exchange',show_lines=True)
			exchange_table.add_column('Name')
			
			for column in previous_exchanges.columns:
				exchange_table.add_column(column.strip('Year_'))
			
			for name in previous_exchanges.index:
				exchange_table.add_row(name,*previous_exchanges.loc[name])
			
			rprint(exchange_table)
			
		except:
			print(previous_exchanges)
	
	#function to create a new window where gifter-giftee assignments
	#from previous years can be added to the database
	def input_previous(self,*args):
		#def add function to kill new window
		#using the after method seems to avoid spinning ball of death on my mac
		def new_window_quit(*args):
			previous_year_window.grab_release()
			previous_year_window.after(10,previous_year_window.destroy)
		
		#def a function on the fly for a new button
		def add_to_exchange(*args):
			if hasattr(self.app.family_tab,'database_file'):
				#get the database fileif hasattr(self.app.family_tab,'database_file'):
				database_file=self.app.family_tab.database_file
			else:
				database_file=os.path.join(self.app.app_directory,'GiftExchange_data',
				    f'data_family_{self.family.get()}','GiftExchange.db')
			
			#make an exchange dictionary
			#this relies on names and name_variables having the same order
			#I need to think about if there is a risk things could get swapped around
			draws=dict((name,variable.get()) for name,variable in\
			    zip(names,name_variables) if variable.get()!='')
			
			add_previous_year(database_file,previous_year.get(),draws)
			
			self.exclude_num_previous_spinbox['to']=max(1,self.get_num_years())
		
		#add a function to check that the names are all in the database
		#or set to NULL
		def check_add_to_exchange_button(*args):
			if valid_year(previous_year.get()):
				state='normal'
				for name in name_variables:
					if not (name.get()=='' or name.get() in names):
						state='disabled'
						break
			else:
				state='disabled'
			
			style=('On.TButton' if state=='normal' else 'Off.TButton')
		
			add_to_exchange_button['state']=state
			add_to_exchange_button['style']=style
		
		#first, get the names
		names=self.app.family_tab.family_member_box['values']
		
		#if the list of names is not empty, open up a new window to fill in
		#previous year exchange info
		if names:
			previous_year_window=tki.Toplevel(self.master)
			previous_year_window.title('Input Previous Draw')
			previous_year_frame=ttk.Frame(previous_year_window)
			
			previous_year=tki.StringVar()
			previous_year_label=ttk.Label(previous_year_frame,text='Year')
			previous_year_entry=ttk.Entry(previous_year_frame,
			    textvariable=previous_year,width=6)
			
			name_variables=[tki.StringVar() for _ in names]
			name_labels=[ttk.Label(previous_year_frame,text=name) for name in names]
			name_entries=[ttk.Entry(previous_year_frame,
			    textvariable=variable,width=12) for variable in name_variables]
			
			add_to_exchange_button=ttk.Button(previous_year_frame,
			    text='Add To Exchange',command=add_to_exchange,state='disabled',
			    style='Off.TButton')
			
			quit_button=ttk.Button(previous_year_frame,text='Close',
			    command=new_window_quit)
			
			#now grid everything
			previous_year_frame.grid(column=0,row=0,sticky='NESW')
			
			previous_year_label.grid(column=0,row=0)
			previous_year_entry.grid(column=1,row=0,sticky='W')
			
			row_idx=1
			for name_label,name_entry in zip(name_labels,name_entries):
				name_label.grid(column=0,row=row_idx)
				name_entry.grid(column=1,row=row_idx,sticky='W')
				row_idx+=1
			
			quit_button.grid(column=0,row=row_idx)
			add_to_exchange_button.grid(column=1,row=row_idx)
			
			previous_year.trace_add('write',check_add_to_exchange_button)
			for name in name_variables:
				name.trace_add('write',check_add_to_exchange_button)
			
			previous_year_window.grab_set()
		
		#if names is empty, nothing to do
		else:
			print(f'Name list for family {self.family.get()} came up empty, nothing to do.')

	#function to set buttons as active or not based on if the family selection
	#is valid or not
	def check_exchange_buttons(self,*args):
		#make sure that the selected family is valid before enabling
		#the draw names button
		button_state=('normal' if self.family.get() in self.get_available_families()\
		    else 'disabled')
	
		button_style=('On.TButton' if button_state=='normal' else 'Off.TButton')
		
		self.draw_names_button['state']=button_state
		self.draw_names_button['style']=button_style
		
		self.skip_members_button['state']=button_state
		self.skip_members_button['style']=button_style
		
		self.view_previous_years_button['state']=button_state
		self.view_previous_years_button['style']=button_style
		
		self.input_previous_year_button['state']=button_state
		self.input_previous_year_button['style']=button_style
		
		self.exclude_num_previous_spinbox['to']=max(1,self.get_num_years())
	
	#function to get the number of years in a database file, skipping the most-recent
	#year, so we can set the maximum number of years used for excludes
	def get_num_years(self,*args):
		#check if a database file has been specified
		if hasattr(self.app.family_tab,'database_file'):
			database_file=self.app.family_tab.database_file
		else:
			database_file=os.path.join(self.app.app_directory,'GiftExchange_data',
			    f'data_family_{self.family.get()}','GiftExchange.db')
		
		if not os.path.exists(database_file):
			return 0
		else:
			return get_num_previous_years(database_file)
	
	#function for quit button, I think using the 'after' method will avoid
	#the GUI hanging up as I'm seeing on my mac
	def quit(self,*args):
		self.master.after(10,self.master.destroy)
		