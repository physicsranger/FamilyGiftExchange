import tkinter as tki
from tkinter import ttk
import time,os

from GiftExchangeUtilities.name_draw import generate_exchange,
    output_giftee_assignments

#make a class for the secondary tab where the past history of the gift exchange
#can be viewed with some logic to hide the most-recent exchange unless
#explicitly asked to show it
class ExchangeTab(ttk.Frame):
	def __init__(self,parent,app,master,*args):
		#do the frame initialization
		ttk.Frame__init__(self)
		
		#assign some attributes so we can access the notebook, app, and Tk instance
		self.parent=parent
		self.app=app
		self.master=master
		
		#add this tab to the notebook
		self.parent.add(self,*args,**kwargs)
		
		self.make_frames()
		
		self.add_traces()
	
	#function to make the main frame and then fill it
	def make_frames(self):
		self.exchange_frame=ttk.Frame(self,borderwidth=1,relief='sunken')
		
		self.fill_exchange_frame(self.exchange_frame)
	
	#function to create the widgets and variables
	#associated with the exchange frame
	def fill_exchange_frame(self,parent):
		#we expect that this should be called after the family frame
		#so we can make it point to the same family variable
		if hasattr(self.app,'family_tab'):
			self.family=self.app.family_tab.family
		else:
			self.family=tki.StringVar()
		
		self.family_label=ttk.Label(parent,text='Family')
		self.family_box=ttk.Combobox(parent,textvariable=self.family)
		self.family_box.bind('<<ComboboxSelected>>',self.get_available_families)
		self.family_box['values']=self.get_available_families()
		
		#button to draw names, start out disabled by default, put a trace
		#on the family variable (can we have multiple traces at once?)
		self.draw_names_button=ttk.Button(parent,text='Draw Names',
		    command=self.draw_names,state='disabled')
		
		self.exclude_num_previous=tki.IntVar(value=3)
		self.exclude_num_previous_label=ttk.Label(parent,
		    text='Number of previous years to exclude giftees')
		self.exclude_num_previous_entry=ttk.Entry(parent,
		    textvariable=self.exclude_num_previous)
		
		self.exchange_year=tki.StringVar(value=time.localtime().tm_year)
		self.exchange_year_label=ttk.Label(parent,text='Year')
		self.exchange_year_entry=ttk.Entry(parent,
		    textvariable=self.exchange_year)
		
		self.overwrite_year=tki.BooleanVar(value=False)
		self.overwrite_year_check=ttk.Checkbutton(parent,
		    variable=self.overwrite_year,onvalue=True,offvalue=False)
		self.overwrite_year_label=ttk.Label(parent,
		    text='Replace existing year.')
		    	
		self.skip_members=[]
		self.skip_members_button=ttk.Button(parent,
		    text='Choose members to skip',command=self.choose_members_to_skip)
		
		self.view_previous_years_button=ttk.Button(parent,
		    text='View Previous Years',command=self.view_previous)
		self.num_previous=tki.IntVar(value=1)
		self.num_previous_label=ttk.Label(parent,text='Number of years to view')
		self.num_prevvious_entry=ttk.Entry(parent,
		    textvariable=self.num_previous,width=4)
		
		self.include_current=tki.BooleanVar(value=False)
		self.include_current_check=ttk.Checkbutton(parent,
		    variable=self.include_current,onvalue=True,offvalue=False)
		self.include_current_label=ttk.Label(parent,text='Include Current')
		
		self.quit_button=ttk.Button(parent,text='Quit',command=self.master.destroy)
	
	def grid_all(self):
		self.grid_exchange()
	
	def grid_exchange(self):
		self.exchange_frame.grid(column=0,row=0,sticky='NESW')
		
		#place widgets within the frame
		self.draw_names_button.grid(column=0,row=0,sticky='W')
		
		self.family_label.grid(column=1,row=0)
		self.family_box.grid(column=2,row=0,sticky='W')
		
		self.exclude_num_previous_label.grid(column=3,row=0,columnspan=2)
		self.exclude_num_previous_entry.grid(column=5,row=0,sticky='W')
		
		self.exchange_year_label.grid(column=0,row=1)
		self.exchange_year_entry.grid(column=1,row=1,sticky='W')
		
		self.overwrite_year_check.grid(column=2,row=1)
		self.overwite_year_label.grid(column=3,row=1)
		
		self.skip_members_button.grid(column=0,row=2,columnspan=2)
		
		self.view_previous_years_button.grid(column=0,row=3)
		self.num_previous_label.grid(column=1,row=3)
		self.num_previous_entry.grid(column=2,row=3,sticky='W')
		
		self.include_current_label.grid(column=3,row=3,sticky='E')
		self.include_current_check.grid(column=4,row=3)
		
		self.quit_button.grid(column=0,row=4)
	
	def add_traces(self,*args):
		self.add_exchange_traces()
	
	def add_exchange_traces(self,*args):
		self.family.trace_add('write',self.check_draw_button)
	
	def draw_names(self,*args):
		if hasattr(self.app.family_tab,'database_file'):
			database_file=self.app.family_tab.database_file.get()
			success=generate_exchange(database_file,
			    skip_names=self.skip_members,
			    num_previous_exclude=self.exclude_num_previous.get(),
			    overwrite=self.overwrite_year.get(),new_year=self.year.get())
		else:
			database_directory=os.path.join(self.app.app_dir,'GiftExchange_data',
			    f'data_family_{self.family.get()}')
				
			database_file=os.path.join(self.database_directory,"GiftExchange.db")
			
			success=generate_exchange(database_file.get(),skip_names=self.skip_members,
			    num_previous_exclude=self.exclude_num_previous.get(),
			    overwrite=self.overwrite_year.get(),new_year=self.year.get())
		
		if success:
			output_giftee_assignments(database_file,self.year.get())
			print(f'Names drawn and assignments generated text files written in {os.path.join(os.path.dirname(database_file),str(year))')
		else:
			print('Could not draw names, examine output for error messages.')
		return
	
	def choose_members_to_skip(self,*args):
		#do stuff
		return
	
	def view_previous(self,*args):
		#do stuff
		return
	
	def check_draw_button(self,*args):
		#make sure that the selected family is valid before enabling
		#the draw names button
		button_state=('normal' if self.family in get_available_families\
		    else 'disabled')
		self.draw_names_button['state']=button_state
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
		
		