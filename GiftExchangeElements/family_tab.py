import tkinter as tki
from tkinter import ttk,filedialog
import os
from gift_exchange_utilities import create_database

#make a class for the main tab where you manage your family database
#and create the gift draws for a given year
class FamilyTab(ttk.Frame):
	def __init__(self,parent,app,master,*args,**kwargs):
		#do the Frame initialization
		ttk.Frame__init__(self)
		
		#assign some attributes so we can access the notebook, app, and Tk instance
		self.parent=parent
		self.app=app
		self.master=master
		
		#add this tab to the notebook
		self.parent.add(self,*args,**kwargs)
		
		self.make_frames()
	
	def make_frames(self):
		#make a frame for the create database button and such
		self.create_frame=ttk.Frame(self)
		self.fill_create_frame(self.create_frame)
		
		#make a frame for entering family info
		self.family_frame=ttk.Frame(self)
		self.fill_family_frame(self.family_frame)
	
	def fill_create_frame(self,parent):
		#first off, button to create an empty database with
		#all the tables we'll want to fill in later
		self.create_button=ttk.Button(parent,text='Create Family',
		command=self.create_family)
		
		#check button to flag if we want to overwrite an existing
		#database of the same name
		self.overwrite=tki.BooleanVar(value=False)
		self.overwrite_check=ttk.Checkbutton(parent,variable=self.overwrite,
		onvalue=True,offvalue=False)
		
		#button to get the directory to save the database in and to
		#know where to look for it...this may be hardcoded later,
		#start with current working directory
		self.database_directory=tki.StringVar(value=os.getcwd())
		self.database_directory_button=ttk.Button(parent,text='Save Location',
		command=self.update_database_directory)
		
		#set a default name, allow for it to be changed
		self.database_file_name=tki.StringVar(value='FamilyGiftExchange.db')
		self.database_file_name_entry=ttk.Entry(parent,
		textvariable=self.database_file_name,width=12)
		
	def fill_family_frame(self,parent):
		#variable, label, and entry for a family member
		
	
	
	
	
	def create_family(self):
		#do stuff
	
	def update_dave_directory(self):
		#do stuff
	
	
		
		
		
		
