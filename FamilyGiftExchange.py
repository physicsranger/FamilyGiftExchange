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

#class for an output text terminal
class TermOut:
        def __init__(self,textwidget):
                self.twidget=textwidget

        def write(self,text):
                self.twidget['state']='normal'
                self.twidget.insert('end',text)
                self.twidget['state']='disabled'
                self.twidget.see("end")

        def flush(self):
                pass

class MainApp:
	def __init__(self,master):
		self.master=master
		
		#I'm going to need to play around with this a little
		#to get things right
		if getattr(sys,'frozen',False):
			self.app_directory=os.path.dirname(sys.executable)
			while self.app_directory.split(os.sep)[-1]!='FamilyGiftExchange'\
			 and self.app_directory!=os.sep:
			 
				self.app_directory=os.path.dirname(self.app_directory)
				
			if self.app_directory==os.sep:
				#couldn't figure out the install dir, use current dir
				self.app_directory=os.getcwd()
			
		elif __file__:
			self.app_directory=os.path.dirname(__file__)
		else:
			self.app_directory=os.getcwd()
		
		self.off_style=ttk.Style()
		self.off_style.configure('Off.TButton',background='darkgray',foreground='gray',
		    font=('Times New Roman',8))
		
		self.on_style=ttk.Style()
		self.on_style.configure('On.TButton',background='gray',foreground='white',
		    font=('Times New Roman',12,'bold'))
		
		self.notebook=ttk.Notebook(self.master)
		
		self.make_tabs()
		
		self.terminal=tki.Text(self.master,state='disabled',height=24,
		    wrap='char',padx=5,pady=5,relief='raised',borderwidth=2)

		self.text_y_scroll=ttk.Scrollbar(self.master,orient='vertical',
            command=self.terminal.yview)
		self.text_x_scroll=ttk.Scrollbar(self.master,orient='horizontal',
		    command=self.terminal.xview)

		self.terminal['yscrollcommand']=self.text_y_scroll.set

		#take care of stdout and stderr...
		#not sure if we'll ever use the saved 'old' versions
		self.old_stdout=sys.stdout
		self.old_stderr=sys.stderr
        
		#create a terminal window
		self.terminal_window=TermOut(self.terminal)
		
		self.construct()
		
		#at the very last assign stdout and stderr to the terminal window, otherwise
        #we miss important code errors
		sys.stdout=self.terminal_window
		sys.stderr=self.terminal_window
	
	def make_tabs(self):
		self.family_tab=FamilyTab(self.notebook,self,self.master,
		    text='Manage Your Family')
		
		self.exchange_tab=ExchangeTab(self.notebook,self,self.master,
		    text='Manage Name Draws')

	def construct(self):
		#set parameters for resizing
		self.master.columnconfigure(0,weight=1)
		self.master.rowconfigure(1,weight=1)
		
		#use grid for the notebook and terminal and the tabs
		self.notebook.grid(column=0,row=0,sticky='NESW')
		#self.notebook.columnconfigure(0,weight=1)
		
		self.terminal.grid(column=0,row=1,sticky='NESW')
		#self.terminal.columnconfigure(0,weight=1)
		
		self.text_y_scroll.grid(column=1,row=1,sticky='NES')
		self.text_x_scroll.grid(column=0,row=2,columnspan=2,sticky='EW')
		
		#use pack for the tabs inside the notebook
		self.family_tab.pack_all()
		
		self.exchange_tab.pack_all()
		
		



#function to be called when the eventual executable/script is called
#will create app as a MainApp instance
def main():
	root=tki.Tk()
	root.title('Family Gift Exchange')
	app=MainApp(root)
	root.mainloop()


if __name__=='__main__':
	main()