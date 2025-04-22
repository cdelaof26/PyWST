# PyWST

**Py** **W**ebScript **T**ranscriptor is a 
pure-python HTML to JavaScript transcriptor.

Its main goal is to provide a way to create 
reusable HTML components for static pages.

### Copyright

<pre>
MIT License

Copyright (c) 2025 @cdelaof26

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
</pre>

### Requirements

- Python >= 3.9

### Usage

```bash
# Clone this repo
git clone https://github.com/cdelaof26/PyWST.git

# Move inside the directory
cd PyWST

# Transcribe a file
python3 main.py path/to/file.html

# Transcribe a bunch of files
python3 main.py path/with/html_files/
```

### Settings

Currently there are only three modificable parameters 
(source modification [WIP]) in `utilities.py`:
- `ALLOW_ANYTHING_IN_CLOSE_TAGS`
- `IGNORE_MISMATCHING_CLOSING_TAGS`
- `MINIFY_CODE`

### Versioning

#### v0.0.4 JS Transcriptor
- Transcription of single and multiple files
- Improved self-closing tag detection
- Improved error messages

#### v0.0.3 Tweaks and fixes
- Handled several edge cases
- Improved error messages

#### v0.0.2 Tag tokenizer

#### v0.0.1 Initial project
