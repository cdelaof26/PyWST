# PyWST

**Py** **W**ebScript **T**ranscriptor is a 
pure-python HTML to JavaScript transcriptor.

Its main goal is to provide a way to create 
reusable HTML components for static pages.

### Requirements

- Python >= 3.9
- `config.py` requires [Questionary](https://github.com/tmbo/questionary.git)

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
# Install the dependencies
python3 -m pip install -r config_requirements.txt

# Create a config file
python3 config.py

# Use PyWST with a config file [WIP]
python3 main.py -c path/to/config
```

### Settings

Currently, there are four modificable parameters 
(through source modification [WIP]) in `utilities.py`:
- `ALLOW_ANYTHING_IN_CLOSE_TAGS`
- `IGNORE_MISMATCHING_CLOSING_TAGS`
- `AUTOMATICALLY_DECODE_HTML_ENTITIES`
- `MINIFY_CODE`

Config files can be created using `config.py`, 
those files will allow PyWST to remember specific 
options for different sets of files [WIP].

`config.py` provides an interactive way to create 
those files, however, [sample](sample) contains more
information about all available options.

### License

Licensed under the [MIT License](LICENSE). Copyright 2025 @cdelaof26.

### Versioning

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
