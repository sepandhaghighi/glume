<div align="center">
<img src="https://github.com/sepandhaghighi/glume/raw/main/otherfiles/logo.png" width="320">
<h1>Glume: A Nano File-to-Text Packer for LLM Context Windows</h1>
<br/>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/built%20with-Python3-green.svg" alt="built with Python3"></a>
<a href="https://github.com/sepandhaghighi/glume"><img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/sepandhaghighi/glume"></a>
<a href="https://badge.fury.io/py/glume"><img src="https://badge.fury.io/py/glume.svg" alt="PyPI version"></a>
</div>			
				
## Overview	

<p align="justify">
Glume is a lightweight Python tool for packing project files into a
structured text representation optimized for LLM context windows.
It collects readable files from a target directory and combines their contents into
a single formatted output, including an optional directory structure
tree.

Glume supports customizable Jinja2 templates, glob-based ignore
patterns, automatic gitignore integration, and file processing
statistics. It can be used both as a CLI tool and as an importable
Python library.
</p>

<table>
	<tr>
		<td align="center">PyPI Counter</td>
		<td align="center"><a href="http://pepy.tech/project/glume"><img src="http://pepy.tech/badge/glume"></a></td>
	</tr>
	<tr>
		<td align="center">Github Stars</td>
		<td align="center"><a href="https://github.com/sepandhaghighi/glume"><img src="https://img.shields.io/github/stars/sepandhaghighi/glume.svg?style=social&label=Stars"></a></td>
	</tr>
</table>



<table>
	<tr> 
		<td align="center">Branch</td>
		<td align="center">main</td>	
		<td align="center">dev</td>	
	</tr>
	<tr>
		<td align="center">CI</td>
		<td align="center"><img src="https://github.com/sepandhaghighi/glume/actions/workflows/test.yml/badge.svg?branch=main"></td>
		<td align="center"><img src="https://github.com/sepandhaghighi/glume/actions/workflows/test.yml/badge.svg?branch=dev"></td>
	</tr>
</table>

## Installation		

### Source Code
- Download [Version 0.1](https://github.com/sepandhaghighi/glume/archive/v0.1.zip) or [Latest Source](https://github.com/sepandhaghighi/glume/archive/dev.zip)
- `pip install .`				

### PyPI

- Check [Python Packaging User Guide](https://packaging.python.org/installing/)     
- `pip install glume==0.1`						


## Usage

Glume can be used both as a CLI tool and as a Python library.

### CLI

``` bash
python -m glume
```

Pack a specific directory:

``` bash
python -m glume ./my-project
```

Save the packed output to a file:

``` bash
python -m glume ./my-project -o context.txt
```

#### Options

| Option           | Description                                               | Default           |
| ---------------- | --------------------------------------------------------- | ----------------- |
| `directory`      | Target directory to pack                                  | `.`               |
| `-o, --output`   | Output file path                                          | Standard output   |
| `-t, --template` | Path to a custom Jinja2 template file                     | Built-in template |
| `--no-tree`      | Disable directory structure tree inclusion                | Enabled           |
| `-i, --ignore`   | Glob patterns to ignore (can be used multiple times)      | None              |
| `--git-ignore`   | Load and apply rules from the project's `.gitignore` file | Disabled          |
| `-v, --verbose`  | Display warnings for unreadable files                     | Disabled          |
| `--stats`        | Display detailed file processing statistics               | Disabled          |

### Library

``` python
from glume import Glume

packer = Glume(
    target_dir="./my-project",
    ignore_patterns=["*.pyc", "__pycache__"],
    use_gitignore=True,
    include_tree=True,
    verbose=False
)

result = packer.pack()

with open("context.txt", "w", encoding="utf-8") as f:
    f.write(result)
```

#### Parameters

| Parameter         | Type                  | Description                                                      | Default           |
| ----------------- | --------------------- | ---------------------------------------------------------------- | ----------------- |
| `target_dir`      | `str` or `Path`       | Root directory containing files to pack                          | `"."`             |
| `custom_template` | `str` or `None`       | Custom Jinja2 template string for rendering the output           | Built-in template |
| `ignore_patterns` | `list[str]` or `None` | Glob patterns for files and directories to ignore                | `None`            |
| `use_gitignore`   | `bool`                | Load ignore patterns from the root directory's `.gitignore` file | `False`           |
| `include_tree`    | `bool`                | Include the directory structure tree in the output               | `True`            |
| `verbose`         | `bool`                | Display warnings when files cannot be read                       | `False`           |

#### Statistics

You can retrieve file processing statistics after packing:

``` python
stats = packer.get_stats()

print(stats["included_count"])
print(stats["ignored_count"])
print(stats["binary_count"])
print(stats["failed_count"])
```

#### Custom Template

Glume supports custom Jinja2 templates for formatting the packed output.

``` python
custom_template = """
{% for file in files %}
### {{ file.path }}

{{ file.content }}
{% endfor %}
"""

packer = Glume(
    target_dir="./my-project",
    custom_template=custom_template
)

result = packer.pack()
```

## Issues & Bug Reports			

Just fill an issue and describe it. We'll check it ASAP!

- Please complete the issue template

## Show Your Support
								
<h3>Star This Repo</h3>					

Give a ⭐️ if this project helped you!

<h3>Donate to Our Project</h3>	

<h4>Bitcoin</h4>
1KtNLEEeUbTEK9PdN6Ya3ZAKXaqoKUuxCy
<h4>Ethereum</h4>
0xcD4Db18B6664A9662123D4307B074aE968535388
<h4>Litecoin</h4>
Ldnz5gMcEeV8BAdsyf8FstWDC6uyYR6pgZ
<h4>Doge</h4>
DDUnKpFQbBqLpFVZ9DfuVysBdr249HxVDh
<h4>Tron</h4>
TCZxzPZLcJHr2qR3uPUB1tXB6L3FDSSAx7
<h4>Ripple</h4>
rN7ZuRG7HDGHR5nof8nu5LrsbmSB61V1qq
<h4>Binance Coin</h4>
bnb1zglwcf0ac3d0s2f6ck5kgwvcru4tlctt4p5qef
<h4>Tether</h4>
0xcD4Db18B6664A9662123D4307B074aE968535388
<h4>Dash</h4>
Xd3Yn2qZJ7VE8nbKw2fS98aLxR5M6WUU3s
<h4>Stellar</h4>		
GALPOLPISRHIYHLQER2TLJRGUSZH52RYDK6C3HIU4PSMNAV65Q36EGNL
<h4>Zilliqa</h4>
zil1knmz8zj88cf0exr2ry7nav9elehxfcgqu3c5e5
<h4>Coffeete</h4>
<a href="http://www.coffeete.ir/opensource">
<img src="http://www.coffeete.ir/images/buttons/lemonchiffon.png" style="width:260px;" />
</a>

