try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

class CheckboxList(object):
	def __init__(self, parent, controller, title, options, row, column, columnspan=1):
		self.options = options
		self.select_all_selected = BooleanVar()

		lf_options = tk.LabelFrame(parent, text=title, padx=15, font='Helvetica 14 bold')
		lf_options.grid(row=row+1, column=column, columnspan=columnspan, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		lf_options.grid_rowconfigure(0, weight=1)
		lf_options.grid_columnconfigure(0, weight=1)

		row = 0

		lb_select_all = Label(lf_options, text='Select all', font='Helvetica 13 bold')
		lb_select_all.grid(row=row, column=0, sticky="W", pady=3)

		self.chk_select_all = tk.Checkbutton(lf_options, variable=self.select_all_selected, command=lambda: self.selectAllOptions())
		self.chk_select_all.grid(row=row, column=1, sticky='W', pady=3)

		row += 1

		self.canvas = Canvas(lf_options)
		self.canvas.grid(row=row, column=0, sticky='nwes')

		vsbar = Scrollbar(lf_options, orient="vertical", command=self.canvas.yview)
		vsbar.grid(row=row, column=1, sticky='ns')
		self.canvas.configure(yscrollcommand=vsbar.set)

		self.frame_buttons = tk.Frame(self.canvas, relief=GROOVE)
		self.frame_buttons.grid(row=0, column=0, sticky='nwes')
		self.canvas_frame = self.canvas.create_window((0,0), window=self.frame_buttons, anchor='nw')
		self.canvas.bind('<Configure>', self.frameWidth)
		self.frame_buttons.bind("<Configure>", self.resize)


		row += 1
		for option in options:
			lb_option = Label(self.frame_buttons, text=option.name.ljust(45))
			lb_option.grid(row=row, column=0, sticky='w', pady=3)

			chk_option = Checkbutton(self.frame_buttons, variable=option.value)
			chk_option.grid(row=row, column=1, sticky='e', pady=3)
			row += 1

	def frameWidth(self, event):
		canvas_width = event.width
		self.canvas.itemconfig(self.canvas_frame, width = canvas_width)

	def resize(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=235, height=190)

	def selectAllOptions(self):
		flag = self.select_all_selected.get()
		for option in self.options:
			option.value.set(flag)


