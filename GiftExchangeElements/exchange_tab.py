import tkinter as tki
from tkinter import ttk
import time,os,glob
import pandas as pd

from functools import reduce

from GiftExchangeUtilities.name_draw import generate_exchange,\
    output_giftee_assignments,get_previous_years,valid_year

#make a class for the secondary tab where the past history of the gift exchange
#can be viewed with some logic to hide the most-recent exchange unless
#explicitly asked to show it
class ExchangeTab(ttk.Frame):
	def __init__(self,parent,app,master,*args,**kwargs):
		#do the frame initialization
		ttk.Frame.__init__(self)
		
		#assign some attributes so we can access the notebook, app, and Tk instance
		self.parent=parent
		self.app=app
		self.master=master
		
		self.get_available_families=self.app.family_tab.get_available_families
		
		#add this tab to the notebook
		self.parent.add(self,*args,**kwargs)
		
		self.make_frames()
		
		self.add_traces()
	
	#function to make the main frame and then fill it
	def make_frames(self):
		self.exchange_frame=ttk.Frame(self,borderwidth=1,relief='sunken')
		
		#self.fill_exchange_frame(self.exchange_frame)
		self.first_row=ttk.Frame(self.exchange_frame,borderwidth=1,relief='flat')
		self.fill_first_row(self.first_row)
		
		self.second_row=ttk.Frame(self.exchange_frame,borderwidth=1,relief='flat')
		self.fill_second_row(self.second_row)
		
		self.third_row=ttk.Frame(self.exchange_frame,borderwidth=1,relief='flat')
		self.fill_third_row(self.third_row)
		
		self.fourth_row=ttk.Frame(self.exchange_frame,borderwidth=1,relief='flat')
		self.fill_fourth_row(self.fourth_row)
		
		self.fifth_row=ttk.Frame(self.exchange_frame,borderwidth=1,relief='flat')
		self.fill_fifth_row(self.fifth_row)
	
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
		
		self.family_label=ttk.Label(parent,text='Family:',
		padding=(2,1,1,1))
		self.family_box=ttk.Combobox(parent,textvariable=self.family,
		    width=14)
		self.family_box.bind('<<ComboboxSelected>>',self.get_available_families)
		self.family_box['values']=self.get_available_families()
		
		self.exclude_num_previous=tki.IntVar(value=3)
		self.exclude_num_previous_label=ttk.Label(parent,
		    text='Number of previous years to exclude giftees',
		    padding=(2,1,1,1))
		self.exclude_num_previous_entry=ttk.Entry(parent,
		    textvariable=self.exclude_num_previous,width=2)
	
	def fill_second_row(self,parent):
		self.exchange_year=tki.StringVar(value=time.localtime().tm_year)
		self.exchange_year_label=ttk.Label(parent,text='Year:',width=4)
		self.exchange_year_entry=ttk.Entry(parent,
		    textvariable=self.exchange_year,width=4)
		
		self.overwrite_year=tki.BooleanVar(value=False)
		self.overwrite_year_check=ttk.Checkbutton(parent,
		    variable=self.overwrite_year,onvalue=True,offvalue=False)
		self.overwrite_year_label=ttk.Label(parent,
		    text='Replace existing year?')
		    	
		self.skip_members=[]
		self.skip_members_button=ttk.Button(parent,
		    text='Choose members to skip',command=self.choose_members_to_skip,
		    state='disabled',style='Off.TButton')	
	
	def fill_third_row(self,parent):
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
	
	def fill_fourth_row(self,parent):
		self.input_previous_year_button=ttk.Button(parent,
		   text='Input Data For Previous Year',command=self.input_previous,
		   state='disabled',style='Off.TButton')
	
	def fill_fifth_row(self,parent):
		self.quit_button=ttk.Button(parent,text='Quit',command=self.quit)
	
	def pack_all(self):
		self.exchange_frame.pack(expand=True,fill='both')
		
		self.pack_first_row()
		self.pack_second_row()
		self.pack_third_row()
		self.pack_fourth_row()
		self.pack_fifth_row()
	
	def pack_first_row(self):
		self.first_row.pack(side='top',fill='x')
		self.draw_names_button.pack(side='left')
		self.family_label.pack(side='left',padx=(8,0))
		self.family_box.pack(side='left',padx=(0,8))
		self.exclude_num_previous_label.pack(side='left')
		self.exclude_num_previous_entry.pack(side='left')
		
	def pack_second_row(self):
		self.second_row.pack(side='top',fill='x')
		self.exchange_year_label.pack(side='left')
		self.exchange_year_entry.pack(side='left')
		self.overwrite_year_label.pack(side='left',padx=(8,0))
		self.overwrite_year_check.pack(side='left',padx=(0,8))
		self.skip_members_button.pack(side='left')
	
	def pack_third_row(self):
		self.third_row.pack(side='top',fill='x',pady=(8,8))
		self.view_previous_years_button.pack(side='left')
		self.num_previous_label.pack(side='left',padx=(8,0))
		self.num_previous_entry.pack(side='left',padx=(0,8))
		self.include_current_label.pack(side='left')
		self.include_current_check.pack(side='left')
	
	def pack_fourth_row(self):
		self.fourth_row.pack(side='top',fill='x',pady=(8,8))
		self.input_previous_year_button.pack(side='left')
	
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
		self.family.trace_add('write',self.check_exchange_buttons)
	
	#function to do the name draw
	def draw_names(self,*args):
		#make sure we have the database file
		if hasattr(self.app.family_tab,'database_file'):
			database_file=self.app.family_tab.database_file
		else:
			database_directory=os.path.join(self.app.app_dir,'GiftExchange_data',
			    f'data_family_{self.family.get()}')
				
			database_file=os.path.join(self.database_directory,"GiftExchange.db")
			
		success=generate_exchange(database_file,skip_names=self.skip_members,
		    num_previous_exclude=self.exclude_num_previous.get(),
		    overwrite=self.overwrite_year.get(),new_year=self.year.get())
		
		if success:
			output_giftee_assignments(database_file,self.year.get())
			print(f'Names drawn and assignments generated text files written\
			 in {os.path.join(os.path.dirname(database_file),str(year))}')
		else:
			print('Could not draw names, examine output for error messages.')
		return
	
	#function to designate family members to not be included in a draw for a given year
	#this will be done by creating a bunch of check boxes to select
	def choose_members_to_skip(self,*args):
		#try creating a function dynamically for the button on this window
		def assign_skip_names(*args):
			self.skip_members=[name for name,flag in zip(names,name_flags) if flag]
			skip_window.destroy()
		
		#get the family member names from the family_tab
		names=self.app.family_tab.family_box['values']
		
		#if the list of names is not empty
		if names:
			#make a popup window for selecting people to exclude
			skip_window=tki.Toplevel(self.master)
			skip_frame=ttk.Frame(skip_window,borderwidth=1,relief='raised')
			skip_label=ttk.Label(skip_frame,text='Skip?')
			
			#make flags for each name
			name_flags=[tki.BooleanVar(value=(False if name not in self.skip_members\
			     else True)) for _ in names]
			#make checkbuttons for each name
			name_checks=[ttk.Checkbutton(skip_frame,variable=name_flag,
			    onvalue=True,offvalue=False) for flag in name_flags]
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
			
			submit_button.grid(column=0,row=row_idx,columnspan=2)
			
			skip_window.grab_set()
		
		#if names is empty, nothing to do
		else:
			print(f'Name list for family {self.family.get()} came up empty,\
			 nothing to do.')
		
	#function to view exchange draws for previous years by popping out
	#another window
	def view_previous(self,*args):
		if hasattr(self.app.family_tab,'database_file'):
			database_file=self.app.family_tab.database_file.get()
		else:
			database_file=os.path.join(self.app.app_dir,'GiftExchange_data',
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
		#try to put tabulate as a dependency, but just in case
		#we'll attempt to catch that error
		try:
			print(previous_exchanges.to_markdown())
		except ImportError:
			print(previous_exchanges)
	
	def input_previous(self,*args):
		#def add function to kill new window
		#using the after method seems to avoid spinning ball of death on my mac
		def new_window_quit(*args):
			previous_year_window.after(10,previous_year_window.destroy)
		
		#def a function on the fly for a new button
		def add_to_exchange(*args):
			if hasattr(self.app.family_tab,'database_file'):
				#get the database fileif hasattr(self.app.family_tab,'database_file'):
				database_file=self.app.family_tab.database_file.get()
			else:
				database_file=os.path.join(self.app.app_dir,'GiftExchange_data',
				    f'data_family_{self.family.get()}','GiftExchange.db')
			
			#make an exchange dictionary
			#this relies on names and name_variables having the same order
			#I need to think about if there is a risk things could get swapped around
			draws=dict((name,variable.get()) for name,variable in\
			    zip(names,name_variables))
			
			add_previous_year(database_file,previous_year.get(),draws)
		
		#add a function to check that the names are all in the database
		#or set to NULL
		def check_add_to_exchange_button(*args):
			if valid_year(previous_year.get()):
				state='normal'
				for name in name_variables:
					if not (name.get().lower=='null' or name.get() in names):
						state='disabled'
						break
			else:
				state='disabled'
			
			style=('On.TButton' if state=='normal' else 'Off.TButton')
		
			add_to_exchange_button['state']=state
			add_to_exchange_button['style']=style
		
		#first, get the names
		names=self.app.family_tab.family_box['values']
		
		#if the list of names is not empty, open up a new window to fill in
		#previous year exchange info
		if names:
			previous_year_window=tki.Toplevel(self.master)
			previous_year_frame=ttk.Frame(previous_year_window)
			
			previous_year=tki.StringVar()
			previous_year_label=ttk.Label(previous_year_frame,text='Year')
			previous_year_entry=ttk.Entry(previous_year_frame,
			    textvariable=previous_year,width=6)
			
			name_variables=[tki.StringVar(value='NULL') for _ in names]
			name_labels=[ttk.Label(previous_year_frame,text=name) for name in names]
			name_entries=[ttk.Entry(previous_year_frame,
			    textvariable=variable,width=12) for variable in name_variables]
			
			add_to_exchange_button=ttk.Button(previous_year_frame,
			    text='Add To Exchange',command=add_to_exchange,state='disabled',
			    style='Off.TButton')
			
			quit_button=ttk.Button(previous_year_frame,command=new_window_quit)
			
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
	
#	#function to list which families are available by investigating
#	def get_available_families(self,*args):
#		#check for available families
#		families=[]
#		if os.path.exists(os.path.join(self.app.app_directory,'GiftExchange_data')):
#			dir_list=glob.glob(os.path.join(self.app.app_directory,
#			'GiftExchange_data','data_family_*'))
#
#			if dir_list:
#				#we want to split on the underscore
#				#but allow for underscores in family names
#				families=[reduce(lambda s1,s2:s1+'_'+s2,\
#				    dir_name.split(os.sep)[-1].split('_')[2:]) for dir_name in dir_list]
#		
#		return families
	
	#function for quit button, I think using the 'after' method will avoid
	#the GUI hanging up as I'm seeing on my mac
	def quit(self,*args):
		self.master.after(10,self.master.destroy)
		