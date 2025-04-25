# PyWST

**Py** **W**ebScript **T**ranscriptor is a 
pure-python HTML to JavaScript transcriptor.

Its main goal is to provide a way to create 
reusable HTML components for static pages.

### Requirements

- Python >= 3.9
- `config.py` requires [Questionary](https://github.com/tmbo/questionary.git)
- Some functions in `main.py` require [watchdog](https://github.com/gorakhargosh/watchdog)
  - watchdog might require Python >= 3.10

### Usage

```bash
# Clone this repo
git clone https://github.com/cdelaof26/PyWST.git

# Move inside the directory
cd PyWST
```

#### Using PyWST

```bash
# Transcribe a file
python3 main.py path/to/file.html

# Transcribe a bunch of files
python3 main.py path/with/html_files/
```

#### Using PyWST with options

```bash
# Move inside the config directory
# (assuming you are in PyWST)
cd config

# Install the dependencies
python3 -m pip install -r config_requirements.txt

# Create a config file
python3 config.py

# Use PyWST with a config file
python3 main.py -c path/to/config
```

### Settings

Config files can be created using `config.py`, 
these files will allow PyWST to process different 
sets of files with specific options.

`config.py` provides an interactive way to create 
those files, however, [sample](config/sample) contains more
information about all available options.

### License

Licensed under the [MIT License](LICENSE). Copyright 2025 @cdelaof26.

### Versioning

#### v0.0.7 File watcher

#### v0.0.6 Config parser
- Created config parser
- Implemented configuration functions
  - WIP: File watcher
- Fixed minor issues with `config.py`

#### v0.0.5-1 Improved project structure

#### v0.0.5 Config creator module
- Added `AUTOMATICALLY_DECODE_HTML_ENTITIES` option

#### v0.0.4 JS Transcriptor
- Transcription of single and multiple files
- Improved self-closing tag detection
- Improved error messages

#### v0.0.3 Tweaks and fixes
- Handled several edge cases
- Improved error messages

#### v0.0.2 Tag tokenizer

#### v0.0.1 Initial project
