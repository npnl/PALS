try:
	import Tkinter as tk
	from Tkinter import *
except ImportError:
	import tkinter as tk
	from tkinter import *

class NameVarStore(object):
	def __init__(self, controller, name, dtype='var', default_value=False):
		self.name = name
		self.value = None
		self.controller = controller
		self.assignVariable(dtype, default_value)

	def assignVariable(self, dtype, default_value):
		if dtype == 'bool':
			value = BooleanVar(self.controller)
			value.set(False)
		else:
			value = Variable(self.controller)
			value.set(default_value)
		self.value = value