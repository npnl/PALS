try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

from .entry_placeholder import EntryWithPlaceholder
import difflib

class CheckboxList(object):
	def __init__(self, parent, controller, title, options, row, column, columnspan=1, user_agreed=None):
		self.options = options
		self.select_all_selected = BooleanVar()
		self.sv_search_string = StringVar()

		self.lf_options = LabelFrame(parent, text=title, padx=15, font='Helvetica 14 bold')
		self.lf_options.grid(row=row+1, column=column, columnspan=columnspan, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
		self.lf_options.grid_rowconfigure(0, weight=1)
		self.lf_options.grid_columnconfigure(0, weight=1)

		row = 0

		wrapper = Frame(self.lf_options)
		wrapper.grid(row=row, column=0, sticky='WE')
		wrapper.grid_rowconfigure(0, weight=1)
		wrapper.grid_columnconfigure(2, weight=1)

		lb_select_all = Label(wrapper, text='Select all', font='Helvetica 13 bold')
		lb_select_all.grid(row=0, column=1, sticky="W", pady=3)

		self.chk_select_all = Checkbutton(wrapper, variable=self.select_all_selected, command=lambda: self.selectAllOptions())
		self.chk_select_all.grid(row=0, column=0, sticky='W', pady=3)

		row += 1

		self.canvas = Canvas(self.lf_options)
		self.canvas.grid(row=row, column=0, columnspan=2, sticky='nwes')

		vsbar = Scrollbar(self.lf_options, orient="vertical", command=self.canvas.yview)
		vsbar.grid(row=row, column=2, sticky='ns')
		self.canvas.configure(yscrollcommand=vsbar.set)
		# self.canvas.bind_all("<MouseWheel>", self.mouseWheel)

		self.frame_buttons = Frame(self.canvas, relief=GROOVE)
		self.frame_buttons.grid(row=0, column=0, sticky='nwes')
		self.canvas_frame = self.canvas.create_window((0,0), window=self.frame_buttons, anchor='nw')
		self.canvas.bind('<Configure>', self.frameWidth)
		self.frame_buttons.bind("<Configure>", self.resize)

		self.frame_buttons.grid_rowconfigure(0, weight=1)
		self.frame_buttons.grid_columnconfigure(2, weight=1)

		self.en_search = EntryWithPlaceholder(self.frame_buttons, placeholder="Search String", textvariable = self.sv_search_string, width = 20)
		self.en_search.grid(row=row+1, column=0, columnspan=2, sticky="W", padx=3, pady=3)

		self.en_search.bind('<KeyRelease>', self.showSearchResults)


		row += 2
		self.labels_chk = []
		self.option_dict = {}
		self.option_names = []
		for option in options:
			lb_option = Label(self.frame_buttons, text=option.name)
			lb_option.grid(row=row, column=1, sticky='w', pady=3)

			chk_option = Checkbutton(self.frame_buttons, variable=option.holder)
			chk_option.grid(row=row, column=0, sticky='W', pady=3)

			self.labels_chk.append([lb_option, chk_option])
			self.option_dict[option.name] = option
			self.option_names.append(option.name)

			row += 1

		self.user_agreed = user_agreed
		if self.user_agreed != None:
			self.user_agreed.trace('w', self.userAgreementChange)
			self.toggleChildren()

	# def mouseWheel(self, event):
	# 	self.canvas.yview_scroll(-1*(event.delta/120), "units")

	def reAssignValues(self, name_order_list):
		if len(self.labels_chk) != len(name_order_list):
			return
		for index, name in enumerate(name_order_list):
			self.labels_chk[index][0].config(text=name)
			self.labels_chk[index][0].update()
			self.labels_chk[index][1].config(variable=self.option_dict[name].holder)
			self.labels_chk[index][1].update()

	def showSearchResults(self, *args):
		search_term = self.sv_search_string.get()
		if len(search_term) > 3:
			name_order_list = self.fuzzySearch(search_term)
			self.reAssignValues(name_order_list)
		if len(search_term) == 0:
			self.reAssignValues(self.option_names)

	def fuzzySearch(self, search_term):
		return sorted(self.option_names, key=lambda z: difflib.SequenceMatcher(None, z, search_term).ratio(), reverse=True)


	def userAgreementChange(self, *args):
		self.toggleChildren()

	def toggleChildren(self):
		try:
			if self.user_agreed.get():
				# self.children_enabled = False
				self.enableChildren(self.lf_options.winfo_children())
			else:
				self.disableChildren(self.lf_options.winfo_children())
		except:
			pass

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
			option.set(flag)
