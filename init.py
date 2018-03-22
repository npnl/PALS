try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

import tkFileDialog
import os

from pages import WelcomePage
from pages import DirectoryInputPage
from pages import PerformedOperationsInputPage
from pages import PauseOptionsInputPage
from pages import QualityControlInputPage

LARGE_FONT = ("Verdana", 12)
 
class MainWindow(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		self.title("SRQL")
		# self.geometry("1200x800")

		self.sv_input_dir = StringVar(self)
		self.sv_output_dir = StringVar(self)
  		self.sv_anatomical_id = StringVar(self)
  		self.sv_lesion_mask = StringVar(self)

  		self.run_normalize_status = BooleanVar(self)
  		self.run_wm_correction = BooleanVar(self)
  		self.run_load_calculation = BooleanVar(self)

  		self.sv_bet_id = StringVar(self)
  		self.sv_wm_id = StringVar(self)

  		self.run_bet = BooleanVar(self)
  		self.run_wm = BooleanVar(self)

  		self.no_pause = BooleanVar(self)

  		self.sv_intensity_percent = StringVar(self)

  		self.sv_input_dir.set('')
  		self.sv_output_dir.set('')

  		self.run_normalize_status.set(False)
  		self.run_wm_correction.set(False)
  		self.run_load_calculation.set(False)

  		self.run_bet.set(True)
  		self.run_wm.set(True)
  		self.no_pause.set(False)
  		self.sv_anatomical_id.set('')
  		self.sv_lesion_mask.set('')
  		self.sv_bet_id.set('')
  		self.sv_wm_id.set('')
  		self.sv_intensity_percent.set('5.0')
 
		# this container contains all the pages
		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)
		self.frames = {}
 		
 		frame_number = 0
		for PageType in self.getApplicationPages():
			frame = PageType(container, self, frame_number)
			self.frames[frame_number] = frame
			frame_number += 1
			frame.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)
 
		self.show_frame(0)
 
	def show_frame(self, frame_number):
		if frame_number >= len(self.frames) or frame_number < 0:
			return
		frame = self.frames[frame_number]
		frame.event_generate("<<ShowFrame>>")
		frame.tkraise()
	
	def getApplicationPages(self):
		pages = [WelcomePage, DirectoryInputPage, PerformedOperationsInputPage,\
			PauseOptionsInputPage, QualityControlInputPage] 
		return pages

if __name__ == '__main__':
	app = MainWindow()
	app.mainloop()
