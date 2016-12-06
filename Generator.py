import sublime, sublime_plugin
from sublime import Region
import subprocess
from collections import OrderedDict
import unicodedata

variable_roots = {}

class less_checkCommand(sublime_plugin.EventListener):

	def on_post_save(self, view):
		current_file = view.file_name()
		lint_format = ".less"

		# We first check to see whether we have just saved a LESS
		# file first. If we have, the command will run.
		# Later, we will add this in as a sublime setting so that
		# you can change it to SASS or another preprocessor, and
		# deal with the variable identifier accordingly.
		if current_file.endswith(lint_format):
			line_split.run(self, view)

class line_split:

	def __init__(self, view):
		self.view		= view

	def run(self, view):
		document = view.substr(sublime.Region(0, view.size()))
		lines = document.splitlines()

		class_dictionary = OrderedDict()
		properties_dictionary = OrderedDict()

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

		# Clear out control characters such as \t or \n
		# remove_control_chars(class_dictionary, True)
		# remove_control_chars(properties_dictionary, False)

		variable_root_generator(class_dictionary)
		print(properties_dictionary)


# def remove_control_chars(dictionary, is_classes):

# 	for line in dictionary.items():
# 		dictionary[line[0]] = line[1].strip()

# 	if is_classes:
# 		variable_root_generator(dictionary)

def variable_root_generator(dictionary):
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

	variable_roots = sorted(zip(nest_lines_key, variable_list))
	print('\n'.join('{}: {}'.format(*k) for k in enumerate(variable_roots)))