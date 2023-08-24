try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

class QCPopup(Toplevel, object):
	def __init__(self, controller):
		Toplevel.__init__(self, controller, padx=25, pady=25)
		self.controller = controller

		Label(self, text='By doing this the operations will not pause for Quality Check. Are you sure you want to opt out of QC ?', font=("Helvetica", 16, 'bold')).grid(row=0, columnspan=100, pady=(0, 20), sticky=W+E+N+S)

		btn_ok = Button(self, text='Ok', command=lambda: self.cleanup(False))
		btn_ok.grid(row=2, column=0, sticky='w')
		
		btn_cancel = Button(self, text='Cancel', command=lambda: self.cleanup(True))
		btn_cancel.grid(row=2, column=100, sticky='e')

		self.protocol('WM_DELETE_WINDOW', lambda: self.cleanup(True))


	def cleanup(self, decision):
		self.controller.b_pause_for_qc.set(decision)
		self.destroy()

