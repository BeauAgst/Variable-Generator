import sublime, sublime_plugin
from sublime import Region
import subprocess
from collections import OrderedDict
import unicodedata

class_dictionary = OrderedDict()
properties_dictionary = OrderedDict()

class less_checkCommand(sublime_plugin.EventListener):

	def on_post_save(self, view):
		current_file = view.file_name()
		lint_format = ".less"

		if current_file.endswith(lint_format):
			line_split.run(self, view)

class line_split:

	def __init__(self, view):
		self.view		= view

	def run(self, view):
		document = view.substr(sublime.Region(0, view.size()))
		lines = document.splitlines()

		class_lines = [",", "{", "}"]

		for index, line in enumerate(lines, 1):
			properties_dictionary[index] = line

			for identifier in class_lines:
				if identifier in line:
					class_dictionary[index] = line
					del properties_dictionary[index]
			
			if not line or line.isspace():
				del properties_dictionary[index]


		remove_control_chars(class_dictionary, True)
		remove_control_chars(properties_dictionary, False)


def remove_control_chars(dictionary, is_classes):
	clean_dictionary = OrderedDict()

	for line in dictionary.items():
		clean_dictionary[line[0]] = line[1].strip()

	if is_classes:
		class_dictionary = clean_dictionary
		variable_generator(class_dictionary)
	else:
		properties_dictionary = clean_dictionary


def variable_generator(dictionary):
	variable_partials = []
	variable_list = []

	for line in dictionary.items():
		line_number = line[0]
		class_name = line[1]

		if "{" in class_name: 
			variable_partials.append(class_name)

			if "}" in class_name: 
				variable_list.append(variable_partials)
				variable_partials.pop()
				# For single line properties
				# We need to check for them and pull the data from this line

		elif "}" in class_name:
			variable_list.append(variable_partials)
			variable_partials.pop()

	print('\n'.join('{}: {}'.format(*k) for k in enumerate(variable_list)))
	print(variable_list)