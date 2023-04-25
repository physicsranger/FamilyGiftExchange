import tkinter as tki
from tkinter import ttk
from gift_exchange_utilities import create_database

#make a class for the main tab where you manage your family database
#and create the gift draws for a given year
class FamilyTab(ttk.Frame):
	def __init__(self,parent,app,master,*args):
		#stuff
