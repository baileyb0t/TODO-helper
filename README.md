# TODO-helper
scripts for converting tagged lines in markdown files into a TODO-like system

### basic outline
- provide the tool:
	0. instructions about how task statements should be organized
		- DEFAULT will include:
			1. primary tags (set using "()")
			2. task collection as list in yaml file
			3. if TODO-helper is identifying statements from a given file, then that file's path will be captured as a link and included in the task

			* option to review a given task collection item-by-item and prompt moving items to the list at "WRITE_PATH/primarytag.done"

	1. a line, file, or path to look for handwritten note content matching the [TODO statement format]()
	2. a path to write TODO statements to
		- formatting will be expandable so that statements can be prescriptive about where to put the task
			- For instance, the line "TODO: (reading) layers of bias paper" would result in the item "layers of bias paper" being added to `WRITE_PATH/reading`


```
WRITE_PATH
└── primarytag
    ├── todo.yml
    └── todo.done
```
--- 

### ideas
- about input
	- NOT DEFAULT but possible:
		1. task collection as timestamped entries in dataframe
			* option to collect non-TODO-formatted lines in a file where TODO items were found as unstructured text in a "notes" field. 
	- receive a single line as input and process as a line in a file
	- check a file regularly for new lines
		* multiple ways to do that including 
			1) checking the last modified time, 
			2) hashing the contents and comparing to known
	- environment issues can be polled
		- `brew`, `conda`, or other package updates needed
		- known-broken TODO for outstanding issues you haven't got to yet
		- packages you haven't used ever / last 6 months
	- add support for working with emails like via mutt?
- should evolve so it can write my weekly for me...

---

##### PSEUDOCODE

on input:
- give a line, look for TODO statement format:
	- first token after "TODO" is treated as the primary 
- given a path, look for readable files (.md, .txt, .yml, etc) and then scan the files for TODO statements

- for each identified file, `TODO-helper` will look for lines that contain "TODO" and collect the contents an item to put in your 


