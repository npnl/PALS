try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

class CheckboxList(object):
	def __init__(self, parent, controller, title, options, row, column, columnspan=1, user_agreed=None):
		self.options = options
		self.select_all_selected = BooleanVar()

		self.lf_options = LabelFrame(parent, text=title, padx=15, font='Helvetica 14 bold')
		self.lf_options.grid(row=row+1, column=column, columnspan=columnspan, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		self.lf_options.grid_rowconfigure(0, weight=1)
		self.lf_options.grid_columnconfigure(0, weight=1)

		row = 0

		lb_select_all = Label(self.lf_options, text='Select all', font='Helvetica 13 bold')
		lb_select_all.grid(row=row, column=0, sticky="W", pady=3)

		self.chk_select_all = tk.Checkbutton(self.lf_options, variable=self.select_all_selected, command=lambda: self.selectAllOptions())
		self.chk_select_all.grid(row=row, column=1, sticky='W', pady=3)

		row += 1

		self.canvas = Canvas(self.lf_options)
		self.canvas.grid(row=row, column=0, columnspan=2, sticky='nwes')

		vsbar = Scrollbar(self.lf_options, orient="vertical", command=self.canvas.yview)
		vsbar.grid(row=row, column=2, sticky='ns')
		self.canvas.configure(yscrollcommand=vsbar.set)

		self.frame_buttons = Frame(self.canvas, relief=GROOVE)
		self.frame_buttons.grid(row=0, column=0, sticky='nwes')
		self.canvas_frame = self.canvas.create_window((0,0), window=self.frame_buttons, anchor='nw')
		self.canvas.bind('<Configure>', self.frameWidth)
		self.frame_buttons.bind("<Configure>", self.resize)

		self.frame_buttons.grid_rowconfigure(0, weight=1)
		self.frame_buttons.grid_columnconfigure(0, weight=1)


		row += 1
		for option in options:
			lb_option = Label(self.frame_buttons, text=option.name)
			lb_option.grid(row=row, column=0, sticky='w', pady=3)

			chk_option = Checkbutton(self.frame_buttons, variable=option.value)
			chk_option.grid(row=row, column=1, sticky='e', pady=3, padx=(0, 10))
			row += 1

		self.user_agreed = user_agreed
		if self.user_agreed != None:
			self.user_agreed.trace('w', self.userAgreementChange)
			self.toggleChildren()

	def userAgreementChange(self, *args):
		self.toggleChildren()

	def toggleChildren(self):
		if self.user_agreed.get():
			# self.children_enabled = False
			self.enableChildren(self.lf_options.winfo_children())
		else:
			self.disableChildren(self.lf_options.winfo_children())

	def disableChildren(self, childList):
		for child in childList:
			try:
				self.disableChildren(child.winfo_children())
			except:
				pass
			try:
				child.configure(state='disable')
			except:
				pass

	def enableChildren(self, childList):
		for child in childList:
			try:
				self.enableChildren(child.winfo_children())
			except:
				pass
			try:
				child.configure(state='normal')
			except:
				pass


	def frameWidth(self, event):
		canvas_width = event.width
		self.canvas.itemconfig(self.canvas_frame, width = canvas_width)

	def resize(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=300, height=190)

	def selectAllOptions(self):
		flag = self.select_all_selected.get()
		for option in self.options:
			option.value.set(flag)


