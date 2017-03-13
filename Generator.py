import sublime, sublime_plugin
from sublime import Region
import subprocess
from collections import OrderedDict
from itertools import islice
import re

variable_roots = {}
properties_dictionary = OrderedDict()
overnested_lines = []

class less_checkCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		# Grab the current line-number so that we can change the 
		# variable on this line specifically
		view = self.view
		line = view.line(view.sel()[0].b)
		(row, col) = view.rowcol(line.begin())
		current_line_number = row + 1

		# We first check to see whether the current file format
		# matches a CSS file. If it does, the command will run.
		if format_check(self):
			class_dictionary = line_split.run(self, view)
			text = variable_stem(variable_root(class_dictionary), current_line_number)
			if text:
				view.replace(edit, line, text)
				sublime.status_message("Variable generated, and value copied to clipboard.")
			else:
				sublime.status_message("No property found on this line.")

class nest_checkCommand(sublime_plugin.EventListener):

	def on_post_save(self, view):

		if format_check(self):
			variable_root(line_split.run(self, view))

			if overnested_lines:
				def async_popup(line_number):
					line_number = (str(line_number)[1:-1])

					popup = """
						<style>html,body{{margin: 0; padding: 5px;}} h1{{padding: 0; margin: 0; color: red;}} span{{display: block;}}</style>
						<h1>Warning</h1><span>You've nested 6 times or more. This is occurring on line(s) {}</span>""".format(line_number)

					view.show_popup(popup)

				async_popup(overnested_lines)


class line_split:

	def __init__(self, view):
		self.view		= view

	def run(self, view):
		document = view.substr(sublime.Region(0, view.size()))
		lines = document.splitlines()
		dictionary = OrderedDict()
		class_dictionary = OrderedDict()
		class_lines = ["{", "}"]

		for index, line in enumerate(lines, 1):
			dictionary[index] = line

		# Remove commented lines from our dictionary
		dictionary = strip_comments(dictionary)

		for item in dictionary.items():
			index = item[0]
			line = item[1]

			properties_dictionary[index] = line

			# For every line in the document, we need to grab
			# those that have classes in them. We store those in
			# class_dictionary, and remove them from 
			# properties_dictionary
			for identifier in class_lines:
				if identifier in line:
					class_dictionary[index] = line
					try:
						del properties_dictionary[index]
					except KeyError:
						pass

			# Clear out empty lines			
			if not line or line.isspace():
				del properties_dictionary[index]

		return class_dictionary

import sublime, sublime_plugin
from sublime import Region
import subprocess
from collections import OrderedDict
from itertools import islice
import re

variable_roots = {}
properties_dictionary = OrderedDict()
overnested_lines = []

class less_checkCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		# Grab the current line-number so that we can change the 
		# variable on this line specifically
		view = self.view
		line = view.line(view.sel()[0].b)
		(row, col) = view.rowcol(line.begin())
		current_line_number = row + 1

		# We first check to see whether the current file format
		# matches a CSS file. If it does, the command will run.
		variable_generator_settings = sublime.load_settings("variable-generator.sublime-settings")

		global variable_prefix
		variable_prefix = variable_generator_settings.get("variable_prefix")

		global lint_format
		lint_format = variable_generator_settings.get("file_format")

		current_file = view.file_name()

		if current_file.endswith(lint_format):
			class_dictionary = line_split.run(self, view)
			text = variable_stem(variable_root(class_dictionary), current_line_number)
			if text:
				view.replace(edit, line, text)
				sublime.status_message("Variable generated, and value copied to clipboard.")
			else:
				sublime.status_message("No property found on this line.")

class nest_checkCommand(sublime_plugin.EventListener):

	def on_post_save(self, view):

		variable_generator_settings = sublime.load_settings("variable-generator.sublime-settings")
		
		global variable_prefix
		variable_prefix = variable_generator_settings.get("variable_prefix")

		global lint_format
		lint_format = variable_generator_settings.get("file_format")

		current_file = view.file_name()

		if current_file.endswith(lint_format):
			variable_root(line_split.run(self, view))

			if overnested_lines:
				def async_popup(line_number):
					line_number = (str(line_number)[1:-1])

					popup = """
						<style>html,body{{margin: 0; padding: 5px;}} h1{{padding: 0; margin: 0; color: red;}} span{{display: block;}}</style>
						<h1>Warning</h1><span>You've nested 6 times or more. This is occurring on line(s) {}</span>""".format(line_number)

					view.show_popup(popup)

				async_popup(overnested_lines)


def strip_comments(dictionary):

	stripped_dictionary = OrderedDict()
	add_to_dic = True

	for line in dictionary.items():
		line_number = line[0]
		class_name = line[1].strip()

		if add_to_dic:

			if class_name.startswith("/*"):

				if "*/" in class_name:
					continue

				else:
					add_to_dic = False

			if class_name.startswith("//"):
				continue
				
			elif add_to_dic:
				stripped_dictionary[line_number] = line[1]

		else:

			if "*/" in class_name:
				add_to_dic = True
				continue

	return stripped_dictionary


def variable_root(dictionary):
	variable_partials = []
	variable_list = []
	group_count = -1;
	nest_count_dictionary = {}
	nest_lines_key = []

	global overnested_lines
	overnested_lines = []

	for line in dictionary.items():
		line_number = line[0]
		class_name = line[1]

		if "{" in class_name: 
			# store class-name in variable_partials, 
			# to generated the nested variables
			variable_partials.append(class_name)

			# Calculate the nest level, adding 1 if
			# a new nest is found. 0 means a new nest.
			group_count += 1

			nest_count_dictionary[group_count] = line_number
			# Check for nesting of more than 6 times,
			# and stored in an array to use later.
			if group_count >= 6:
				global overnested_lines
				overnested_lines.append(line_number)

		if "}" in class_name:
			# add array from variable_partials to 
			# variable_list. We will re order these later
			variable_list.append(variable_partials[:])
			variable_partials.pop()

			# For single line properties
			# We need to check for them and pull the data from this line
			# CODE HERE

			# Remove from the dictionary when a nest is closed, and
			# add the line number to nest_lines_key.
			nest_lines_key.append(nest_count_dictionary[group_count])
			del nest_count_dictionary[group_count]

			# We lower the group count AFTER, so that we don't grab the
			# wrong a line that doesn't exist from the dictionary
			group_count -=1

			if group_count == -1:
				# We'll need to clear our arrays here, so that we start
				# fresh for each new nest.
				nest_count_dictionary.clear()

	# We need to return our variable list, but it 
	# needs to be sorted with the line number, otherwise
	# the information is useless to us.
	return sorted(zip(nest_lines_key, variable_list))


def variable_stem(dictionary, current_line):

	for first, next in zip(dictionary, dictionary[1:]):
		first_item = int(first[0])
		next_item = int(next[0])
		last = dictionary[-1][1]
		last_item = int(dictionary[-1][0])
		last_property = list(islice(properties_dictionary, None))[-1:][0]

		# Loop through the entire dictionary list
		# so that we can look for our line
		for item in properties_dictionary.items():

			# Check if our line is between two classes, so 
			# that we can grab the correct variable root
			if current_line in range(first_item, next_item):

				if current_line == item[0]:
					return generate_variable(first[1], item[1])

			# We also need to check between the last item and the 
			# very last property plus one, so that we can grab any 
			# properties that are in the very final nest of the file
			if current_line in range(last_item, last_property+1):

				if current_line == item[0]:
					return generate_variable(last, item[1])


def generate_variable(variable_list, line):
	variable_name = []
	css_property = line.split(":", 1)[0].strip()
	css_value = line.split(":", 1)[1].strip()
	tabs = "\t" * (line.count("\t") - line.lstrip().count("\t"))

	# Check for reponsive hook, and replace with appropriate prefix.
	if "hook-responsive-" in variable_list[0]:
		responsive_prefix = variable_list[0].split("hook-responsive-", 1)[1].split("(", 1)[0]
		variable_list.remove(variable_list[0])

	# Check for regular hooks, and remove that portion of the class. We
	# also need to remove all symbols from the variable, and then 
	# strip whitespace.
	for variable in variable_list:
		variable = variable.replace(".hook-", "")

		if "[" in variable:
			variable_start = variable.split("[")[0]
			variable_end = variable.split("]")[1]
			variable = variable.replace(variable_start, "").replace(variable_end, "").split("=")[1].split("]")[0]
			variable = variable_start +  variable + " " + variable_end

		variable_name.append(re.sub('[^A-Za-z0-9 -]+', '', variable).strip())


	# Join our list together
	variable_name = "-".join(variable_name)
	variable_name = variable_name.replace(" ", "-")

	# If a responsive hook was found, we need to stick it back into the list
	if 'responsive_prefix' in locals():
		variable_name = responsive_prefix + "_" + variable_name

	# Add variable prefix, dependant on preprocessor
	variable_name = variable_prefix + variable_name

	# Add css property
	variable_name = variable_name + "--" + css_property

	sublime.set_clipboard(variable_name + ": " + css_value)
	text = tabs + css_property + ": " + variable_name + ";"
	return text