# Variable Generator #

Variable Generator is a Sublime Text 3 plugin that allows you to convert your CSS into a variables string. The contents of the variable is then copied to your clipboard so that you can place it wherever necessary.

Variables follow this structure: `#hook_element--property_modifier`, where "#" is the variable prefix of your choice. For example if using SASS you find that a homepage jump's title needs a font-size modification in the "sm" hook, it would look like this: `$sm_homepage-jump--font-size`

### Demo ###

![Demonstration of how Blamer works](http://www.beaugust.co.uk/img/demos/var-gen.gif)

### How do I get set up? ###

* Clone project 
* Copy folder to `C:\Users\YOUR NAME\AppData\Roaming\Sublime Text 3\Packages`, where YOUR NAME is replaced with your Users' name
* Restart Sublime.

### How do I use it? ###

Once Sublime Text is open, navigate to Preferences > Package Settings > Variable Generator > Settings - Default. In here you will find 2 options -

* `variable_prefix`: This is the symbol that you'd like to prefix your variable with. Default is "@"
* `file_format`: Set this to the file format that you want to blame. Default is ".less"

Once you have adjusted your preferences, you're all set.

### Shortcuts ###

* `ctrl + f12`: Generates your variable, and copies the variable and its' value to your clipboard.