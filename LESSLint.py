import sublime, sublime_plugin
from sublime import Region
import subprocess

class less_checkCommand(sublime_plugin.EventListener):

	def on_post_save(self, view):
		lint_format = ".less"
		current_file = view.file_name().rsplit("\\", 1)[1]

		if current_file.endswith(lint_format):
			line_split.run(self, view)

class line_split:

	def __init__(self, view):
		self.view		= view

	def run(self, view):
		document = view.substr(sublime.Region(0, view.size()))
		lines = document.splitlines()
		lines_dictionary = {}

		for index, line in enumerate(lines, 1):
			lines_dictionary[index] = line

			if "{" not in line and "}" not in line:
				del lines_dictionary[index]

		nest_count.run(self, view, lines_dictionary)

class nest_count:

	def run(self, view, lines_dictionary):

		def async_popup(line_number):
			top_left = view.layout_to_text((0.0, 0.0))
			popup = """
				<style>html,body{{margin: 0; padding: 2px 5px 5px; background-color: #fafafa;}} h1{{color: red; padding: 0; margin: 0;}} </style>
				<h1>WARNING</h1><span>You have nested 6 times.</span><br><span>This is happening on line {}</span><br><span>This file will fail to compile in Sloth.</span>""".format(line_number)		
			view.show_popup(popup, location=top_left)

		group_count = -1;
		nested_lines = []

		for index, line in lines_dictionary.items():
			lines_dictionary[index] = line

			if "{" in line: 
				group_count += 1

				if group_count >= 6:
					nested_lines.append(index)
				
				if "}" in line: 
					group_count -= 1

			elif "}" in line:
				group_count -= 1

		if nested_lines:
			sublime.set_timeout_async(async_popup(nested_lines))