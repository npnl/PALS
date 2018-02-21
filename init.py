try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os

from pages.directory_input import DirectoryInputPage
from pages.performed_operations_input import PerformedOperationsInputPage

LARGE_FONT = ("Verdana", 12)
 
class MainWindow(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		self.title("SQRL")
		self.geometry("1200x800")

		self.sv_input_dir = StringVar(self)
		self.sv_output_dir = StringVar(self)
  		self.sv_image_iden = StringVar(self)
  		self.sv_lesion_mask_identi = StringVar(self)

  		self.sv_bet_id = StringVar(self)
  		self.sv_wm_id = StringVar(self)

  		self.bet_status = False
  		self.bet_status = False
  		self.bet_status = False

  		self.sv_input_dir.set('')
  		self.sv_output_dir.set('')
  		self.sv_image_iden.set('')
  		self.sv_lesion_mask_identi.set('')
  		self.sv_bet_id.set('')
  		self.sv_wm_id.set('')
 
		# this container contains all the pages
		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)
		self.frames = {}
 
 		frame_number = 0
		for PageType in (DirectoryInputPage, PerformedOperationsInputPage):
			frame = PageType(container, self, frame_number)
			self.frames[frame_number] = frame
			frame_number += 1
			frame.grid(row=0, column=0, sticky="nsew")
 
		self.show_frame(0)
 
	def show_frame(self, frame_number):
		frame = self.frames[frame_number]
		frame.tkraise()
 
if __name__ == '__main__':
	app = MainWindow()
	app.mainloop()
