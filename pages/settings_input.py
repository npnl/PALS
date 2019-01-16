try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from .base_input import *
from utils import isValidPath
import os

class SettingsInput(BaseInputPage, object):
	def __init__(self, parent, controller, frame_number):
		BaseInputPage.__init__(self, parent, controller, frame_number)

		lb_input = Label(self, text=self.controller.sv_fsl_binaries_msg.get())
		lb_input.grid(row=self.starting_row+1, column=0, sticky="W", pady=3)

		

	def setFrameTitle(self):
		self.title.set('Please indicate the following:')