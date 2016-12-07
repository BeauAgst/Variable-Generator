import sublime, sublime_plugin
from sublime import Region
import subprocess
from collections import OrderedDict
from itertools import islice
import re

variable_roots = {}
properties_dictionary = OrderedDict()

class less_checkCommand(sublime_plugin.TextCommand):

	def run(self, view):
		current_file = self.view.file_name()
		lint_format = ".less"

		# Grab the current line-number so that we can change the 
		# variable on this line specifically
		view = sublime.Window.active_view(sublime.active_window())
		(row,col) = view.rowcol(view.sel()[0].begin())
		current_line_number = row + 1

		# We first check to see whether we have just saved a LESS
		# file. If we have, the command will run.
		# Later, we will add this in as a sublime setting so that
		# you can change it to SASS or another preprocessor, and
		# deal with the variable identifier accordingly.
		if current_file.endswith(lint_format):
			class_dictionary = line_split.run(self, view)
			variable_stem(variable_root(class_dictionary), current_line_number)

class line_split:

	def __init__(self, view):
		self.view		= view

	def run(self, view):
		document = view.substr(sublime.Region(0, view.size()))
		lines = document.splitlines()
		class_dictionary = OrderedDict()
		class_lines = [",", "{", "}"]


		# For every line in the document, we need to grab
		# those that have classes in them. We store those in
		# class_dictionary, and remove them from 
		# properties_dictionary
		for index, line in enumerate(lines, 1):
			properties_dictionary[index] = line

			for identifier in class_lines:
				if identifier in line:
					class_dictionary[index] = line
					del properties_dictionary[index]

			# Clear out empty lines			
			if not line or line.isspace():
				del properties_dictionary[index]

		return class_dictionary

def variable_root(dictionary):
	variable_partials = []
	variable_list = []
	group_count = -1;
	nest_count_dictionary = {}
	nest_lines_key = []
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
					generate_variable(first[1], item[1])
					return

			# We also need to check between the last item and the 
			# very last property plus one, so that we can grab any 
			# properties that are in the very final nest of the file
			if current_line in range(last_item, last_property+1):

				if current_line == item[0]:
					generate_variable(last, item[1])
					return


def generate_variable(variable_list, line):

	variable_name = []
	variable_prefix = "@"
	css_property = line.split(":", 1)[0].strip()
	css_value = line.split(":", 1)[1].strip()
	tabs = line.count("\t") - line.lstrip().count("\t")
	hooks = [
		["xxs-max()", "xxs-max_"],
		["xs-max()", "xs-max_"],
		["sm-max()", "sm-max_"],
		["md-max()", "md-max_"],
		["lg-max()", "lg-max_"],
		["xs()", "xs_"],
		["xs-landscape()", "xs-landscape_"],
		["sm()", "sm_"],
		["md()", "md_"],
		["lg()", "lg_"],
		["laptop()", "laptop_"],
		["xl()", "xl_"],
		["sm-only()", "sm-only_"],
		["md-only()", "md-only_"],
		["lg-only()", "lg-only_"],
		["xs-only()", "xs-only_"]
	]

	# Check for reponsive hook, and replace with appropriate prefix.
	for hook in hooks:

		if hook[0] in variable_list[0]:
			responsive_prefix = hook[1]
			variable_list.remove(variable_list[0])
			break

	# Check for regular hooks, and remove that portion of the class. We
	# also need to remove all symbols from the variable, and then 
	# strip whitespace.
	for variable in variable_list:
		variable = variable.replace(".hook-", "")
		variable_name.append(re.sub('[^A-Za-z0-9]+', '', variable))

	# Join our list together
	variable_name = "-".join(variable_name)

	# If a responsive hook was found, we need to stick it back into the list
	if 'responsive_prefix' in locals():
		variable_name = responsive_prefix + variable_name

	# Add variable prefix, dependant on preprocessor
	variable_name = variable_prefix + variable_name

	# Add css property
	variable_name = variable_name + "--" + css_property

	print(variable_name + ": " + css_value)
	print(("\t")*tabs + css_property + ": " + variable_name + ";")
	copy2clip(variable_name + ": " + css_value)

def copy2clip(txt):
	cmd='echo '+txt.strip()+'|clip'
	return subprocess.check_call(cmd, shell=True)