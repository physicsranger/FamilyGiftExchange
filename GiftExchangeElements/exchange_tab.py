import tkinter as tki
from tkinter import ttk

from GiftExchangeUtilities.name_draw import generate_exchange

#make a class for the secondary tab where the past history of the gift exchange
#can be viewed with some logic to hide the most-recent exchange unless
#explicitly asked to show it
class ExchangeTab(ttk.Frame):
	def __init__(self,parent,app,master,*args):
		#do the frame initialization
		ttk.Frame__init__(self)
		
		
		self.parent=parent
		self.app=app
		self.master=master
		self.parent.add(self,*args,**kwargs)
		
		