## Agenda
1. project 1 deliverable progress
2. In-depth code review: project 2
	- what does the code do?
	- what could the code do better?
	- are there any:
		- variable or file names that could be more intuitive?
		- hardcoded statements that should either be an argument or be in a yaml file?
		- methods defined where built-in or library methods would be more effective?
		- manipulations to the data that are not noted in a log file or flanked with assertions/stopifnots?
		- "magic numbers" worth capturing from the output?
- TODO: add the code review prompts to a training doc
- TODO: (longterm) practice R

#### import
- TODO: (project 2) import Makefile targets need better names
- TODO: (project 2) import.R initial_asserts() needs improvement
- TODO: (project 2) import.R apply TS advice about short functions
- TODO: (project 2) sample_state.R apply TS advice about short functions

#### clean
cleaning unstructured text fields (with considerations for database stage)

- should Makefile use sample_state.R output? or continue reading national.parquet?
- TODO: (project 2) clean logical_missing.yaml deprecated?
- TODO: (project 2) clean.py initial_asserts() needs improvement
- TODO: (project 2) clean.py final_asserts() needs improvement
- TODO: (project 2) clean.py apply TS advice about short functions
- TODO: (project 2) clean.py format_str() deprecated?
- TODO: (project 2) clean.py lines 97-106 should be a function

#### canonicalize
had been working on issue related to making database source indicators
- TODO: (project 2) hand asis.yml deprecated?
- TODO: (project 2) canonicalize Makefile compiles?
- TODO: (project 2) canonicalize merge.py implementation
- TODO: (project 2) review definitions set by hand subject_injury.yml
- TODO: (project 2) apply TS advice about short functions
- TODO: (reading) review TS email about time results for other OHE methods
- TODO: (project 2) canonicalize database.py methodology needs improvement

done.
