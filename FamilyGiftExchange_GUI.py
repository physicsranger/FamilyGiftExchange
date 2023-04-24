import tkinter as tki
from tkinter import ttk
import os


'''First we have to make the 'family' table, that will give each person a unique
ID, and then that ID can more easily (safely?) be used for the column name in the 
'exchange' table where the rows are years.  We then can also use those unique identifiers
to create a 'significant_other' table to use in exclusions.  The family table will have
the actual names and email addresses'''

class MainApp:
	def __init__(self,master):
		self.master=master
		self.notebook=ttk.Notebook(self.master)