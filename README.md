# Config Suite TUI

![configsuite-tui](https://github.com/equinor/configsuite-tui/workflows/configsuite-tui/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/59b5a3b6411f4242aaec85370382d35e)](https://www.codacy.com/gh/equinor/configsuite-tui/dashboard?utm_source=github.com&utm_medium=referral&utm_content=equinor/configsuite-tui&utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/59b5a3b6411f4242aaec85370382d35e)](https://www.codacy.com/gh/equinor/configsuite-tui/dashboard?utm_source=github.com&utm_medium=referral&utm_content=equinor/configsuite-tui&utm_campaign=Badge_Coverage)
[![Documentation Status](https://readthedocs.org/projects/config-suite-tui/badge/?version=latest)](https://config-suite-tui.readthedocs.io/en/latest/?badge=latest)

## Introduction

Config Suite TUI is text-based user interface extension for [Config Suite](https://github.com/equinor/configsuite). It provides a simplified, visual way of creating and editing configuration files for a given schema.

![Config Suite TUI Screenshot](https://i.imgur.com/1py3WSl.png)

## Features

-   Simplified editing of configuration files
-   Import and export yaml files
-   Instant validation
-   Plugin system to provide schemas from other python modules

## Documentation

Check out the documentation on [Read the Docs](https://config-suite-tui.readthedocs.io/en/stable/).

## Installation

Installation of Config Suite TUI can easily be done using pip:

```
$ pip install configsuite-tui
```

## Developer guidelines
Contributions to _Config Suite_ is very much welcome! Bug reports, feature requests and improvements to the documentation or code alike. However, if you are planning a bigger chunk of work or to introduce a concept, initiating a discussion in an issue is encouraged.

### Running the tests
The tests can be executed with `python -m unittest`.

### Code formatting
The entire code base is formatted with [black](https://black.readthedocs.io/en/stable/).

### Pull request expectations
We expect a well-written explanation for smaller PR's and a reference to an issue for larger contributions. In addition, we expect the tests to pass on all commits and the commit messages to be written in imperative style. For more on commit messages read [this](https://chris.beams.io/posts/git-commit/).

## License

_Config Suite TUI_ is licensed under the MIT License. For more information we refer
the reader to the [LICENSE file](https://github.com/equinor/configsuite-tui/blob/main/LICENSE).
