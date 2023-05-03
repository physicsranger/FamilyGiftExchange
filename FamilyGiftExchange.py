#!/usr/bin/env python
###will the shebang above actually work across operating systems?
import tkinter as tki
from tkinter import ttk
import os,sys
from GiftExchangeElements.family_tab import FamilyTab
from GiftExchangeElements.exchange_tab import ExchangeTab

'''First we have to make the 'family' table, that will give each person a unique
ID, and then that ID can more easily (safely?) be used for the column name in the 
'exchange' table where the rows are years.  We then can also use those unique identifiers
to create a 'significant_other' table to use in exclusions.  The family table will have
the actual names and email addresses'''

class MainApp:
	def __init__(self,master):
		self.master=master
		
		#I'm going to need to play around with this a little
		#to get things right
		if getattr(sys,'frozen',False):
			self.app_directory=os.path.dirname(sys.executable)
			while self.app_directory.split(os.sep)[-1]!='FamilyGiftExchange' and self.app_directory!=os.sep:
				self.app_directory=os.path.dirname(self.app_directory)
		if self.app_directory==os.sep:
			#couldn't figure out the install dir, use current dir
			self.app_directory=os.getcwd()
			
			
		elif __file__:
			self.app_directory=os.path.dirname(__file__)
		else:
			self.app_directory=os.getcwd()
		
		self.notebook=ttk.Notebook(self.master)
		
		self.make_tabs()
		
		self.grid_all()
	
	def make_tabs(self):
		self.family_tab=FamilyTab(self.notebook,self,self.master,
		text='Manage Your Family')
		
		self.exchange_tab=ExchangeTab(self.notebook,self,self.master,text='Gift Exchange')

	def grid_all(self):
		self.family_tab.grid_all()
		
		self.exhange_tab.grid_all()




#function to be called when the eventual executable/script is called
#will create app as a MainApp instance
def main():
	root=tki.Tk()
	app=MainApp(root)
	root.mainloop()


if __name__=='__main__':
	main()