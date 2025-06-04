# PyWST

**Py** **W**ebScript **T**ranscriptor is a 
pure-python HTML to JavaScript transcriptor.

Its main goal is to provide a way to create 
reusable HTML components for static pages, however 
it also can be used to convert web pages into JS.

### Requirements

- Python >= 3.9
- `config.py` requires of [Questionary](https://github.com/tmbo/questionary.git)
- Some functions in `main.py` require of [watchdog](https://github.com/gorakhargosh/watchdog)
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
python3 main.py -f path/to/file.html

# Transcribe a bunch of files
python3 main.py -f path/with/html_files/
```

#### Using PyWST with options

- Configuration file

```bash
# Move inside the config directory
# (assuming you are in PyWST)
cd config

# Install the dependencies
python3 -m pip install -r config_requirements.txt

# Create a config file
python3 config.py

# Use PyWST with a config file
python3 main.py -c -f path/to/config
```

<details>

<summary>CLI parameters</summary>

| Option             | Description                                                               | Value                    | Config file equivalent               | Notes                                                    |
|--------------------|---------------------------------------------------------------------------|--------------------------|--------------------------------------|----------------------------------------------------------|
| `-c` `--config`    | Specifies that the file is a config file                                  | Path to config file      |                                      | If present, any other option will be ignored except `-f` |
| `-f` `--file`      | Config, directory or HTML file path                                       | Path to HTML file        | `FILE` or `PATH` for directories     |                                                          |
| `-b` `--behavior`  | What the script does, return or replace HTMLElements                      | `ret` or `rep`           | `BEHAVIOR`                           | default is `ret`                                         |
| `-id` `--idrepl`   | Replacement ID                                                            | String                   | `REPL_ID`                            |                                                          |
| `-uid` `--uidrepl` | Replacement ID for all components                                         | String                   | `UN_REPL_ID`                         |                                                          |
| `-p` `--params`    | Parameters used inside the HTML                                           | List separated by commas | `PARAMS`                             |                                                          |
| `-o` `--onload`    | Whether the script should run onload                                      | `yes` or `no`            | `ONLOAD`                             | Requires `--behavior rep`, default is `no`               |
| `-w` `--watch`     | Whether PyWST should watch for filesystem changes                         | `yes` or `no`            | `WATCH`                              | default is `no`                                          |
| `-m` `--minify`    | Whether PyWST should minify generated scripts                             | `yes` or `no`            | `MINIFY_CODE`                        | default is `yes`                                         |
| `--ictag`          | Whether PyWST should ignore uncommon characters inside closing tags       | `yes` or `no`            | `ALLOW_ANYTHING_IN_CLOSE_TAGS`       | default is `no`                                          |
| `--mctag`          | Whether PyWST should ignore mismatching closing tags                      | `yes` or `no`            | `IGNORE_MISMATCHING_CLOSING_TAGS`    | default is `no`                                          |
| `--entdec`         | Whether PyWST should add a function to decode HTML entities when detected | `yes` or `no`            | `AUTOMATICALLY_DECODE_HTML_ENTITIES` | default is `yes`                                         |

- Usage examples

```bash
# Watch file.html for changes and disable minifying 
python3 main.py -w yes -m no -f /home/user/file.html

# Ignore invalid characters in closing tags and mismatching closing tags
python3 main.py --ictag yes --mctag yes -f /home/user/generated.html

# Process all files in /home/user/, generated scripts will replace my-component-id
python3 main.py -b rep --idrepl my-component-id -f /home/user/

# Add parameters to the component (script tag will be replaced)
python3 main.py --behavior rep --idrepl "" --params "id, articleTitle, articleText" --file "/home/user/my webpage.html"
```

</details>

### Settings

Configuration files can be created using `config.py`, 
these files will allow PyWST to process different 
sets of files with specific options.

`config.py` provides an interactive way to create 
those files, however, [sample](config/sample) contains more
information about all available options.

### Using events
<details>
<summary>How to use parameters</summary>

To use an event inside a function, said function must have `evt`
as parameter as shown below.

```html
<!-- function_name must receive `evt` as parameter -->
<button onclick="function_name(evt)"></button>
```

```js
// The name in the definition doesn't have to be `evt`
function function_name(myEvent) {
    // Do somthing
}
```
</details>

### Using component parameters

<details>
<summary>How to use parameters</summary>

Parameters can be used inside an HTML by writing `${paramName}` 
inside an attribute or text block, for example:

```html
<!-- MyComponent.html -->

<div id="myDiv">
    <p class="${myClass}">
        ${textAsParameter}
    </p>
</div>
```

To tell PyWST to add those parameters, you will need to 
add `PARAMS` for every `FILE` specified in your config file.

```
# ConfigFile
...
FILE = MyComponent.html
PARAMS = myClass, textAsParameter
...
```

```bash
# Or use --params as CLI parameter 
python3 main.py --params "myClass, textAsParameter" --file MyComponent.html 
```

If you are using `BEHAVIOR = replace`, then the element to 
replace needs to have the parameters and values as attributes 
as following:

```html
<div id="idToReplace" myClass="bg-green-100" textAsParameter="Hello World">
    ...
</div>
```

</details>

### License

Licensed under the [MIT License](LICENSE). Copyright 2025 @cdelaof26.

### Versioning

#### v0.0.9-2 Fixes
- Reduced thread overhead
- Fixed bug where two files with similar name 
  would interfere with each other. 

#### v0.0.9-1 Minor fixes
- Fixed unhandled `AssertionError`
- Fixed `Specified path is not a config file` when a config 
  file is given
- PyWST won't create js files unless some code generation is done
- Handled edge case when the file to process doesn't have 
  a suffix (file extension)

#### v0.0.9 CLI arguments and fixes

#### v0.0.8 Additional configuration and fixes
- Fixed event listeners
- Added component parameters
- Fixed properties of components in a same config block getting
  mixed
- `REPL_ID` is optional in some cases
- Fixed multiple `path` SVG

#### v0.0.7-1 Minor tweaks
- Fixed incorrectly placement of elements if an SVG was involved

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
