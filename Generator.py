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
		remove_control_chars(class_dictionary, True)
		remove_control_chars(properties_dictionary, False)


def remove_control_chars(dictionary, is_classes):

	for line in dictionary.items():
		dictionary[line[0]] = line[1].strip()

	if is_classes:
		class_dictionary = dictionary
		variable_stem_generator(class_dictionary)
	else:
		properties_dictionary = dictionary

def variable_stem_generator(dictionary):
	variable_partials = []
	variable_list = []
	group_count = 0;
	old_group_count = 0;
	nested_lines = []

	for line in dictionary.items():
		line_number = line[0]
		class_name = line[1]

		if "{" in class_name: 
			# store class-name in variable_partials, 
			# to generated the nested variables
			variable_partials.append(class_name)

			# Calculate the nest level, adding 1 if
			# a new nest is found. 0 means a new nest.
			if group_count == 0:
				print("Nest started on line " + str(line_number))

			group_count += 1
			old_group_count += 1

			# Check for nesting of more than 6 times,
			# and stored in an array to use later.
			if group_count >= 7:
				nested_lines.append(line_number)

		if "}" in class_name:
			# add array from variable_partials to 
			# variable_list. We will re order these later
			variable_list.append(variable_partials[:])
			variable_partials.pop()

			# For single line properties
			# We need to check for them and pull the data from this line
			# CODE HERE

			# Remove from the count if a nest is closed.
			# We need to check for paired nest_count values 
			# here as well.
			group_count -=1

			if group_count == 0:
				# We'll need to clear our arrays here, so that we start
				# fresh for each new nest.
				print("Nest ended on line " + str(line_number))

	# print('\n'.join('{}: {}'.format(*k) for k in enumerate(variable_list)))
	print("There are " + str(len(nested_lines)) + " classes that are nested 6 times or more. These can be found on lines " + str(nested_lines))
	print()


# Array 1
# 0: 1
# 1: 4
# 2: 7 
# 3: 9
# 4: 11
# 3: 13
# 4: 15
# 3: 17
# 2: 18
# 1: 19
# 0: 20
# -1: 21


# Array 2
# 0: ['no_nest {', 'nest_1-1 {', 'nest_2 {', 'nest_3 {', 'nest_4-1 {']
# 1: ['no_nest {', 'nest_1-1 {', 'nest_2 {', 'nest_3 {', 'nest_4-2 {']
# 2: ['no_nest {', 'nest_1-1 {', 'nest_2 {', 'nest_3 {']
# 3: ['no_nest {', 'nest_1-1 {', 'nest_2 {']
# 4: ['no_nest {', 'nest_1-1 {']
# 5: ['no_nest {']


# Array 3 
# 0: [1, ['no_nest {']]
# 1: [4, ['no_nest {', 'nest_1-1 {']]
# 2:

# count = -1
# new_count = -1

# count +=1

# if count + 1 == new_count:
# 	pair off
# else count = new_count