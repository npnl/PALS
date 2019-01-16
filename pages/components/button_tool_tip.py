try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from .tool_tip import createToolTip

class ButtonToolTip(tk.Frame, object):
	def __init__(self, master=None, tool_tip_text='', **kwargs):
		tk.Frame.__init__(self, master)

		btn = Button(self, **kwargs)
		btn.grid(row=0, column=0)

		if tool_tip_text != '':
			lb_help = Label(self, text=u'\uFFFD')
			lb_help.grid(row=0, column=1)
			createToolTip(lb_help, tool_tip_text)