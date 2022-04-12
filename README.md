# tap-coingecko

`tap-coingecko` is a Singer tap for Coingecko.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

- [ ] `Developer TODO:` Update the below as needed to correctly describe the install procedure. For instance, if you do not have a PyPi repo, or if you want users to directly install from your git repo, you can modify this step as appropriate.

```bash
pipx install tap-coingecko
```

## Configuration

### Accepted Config Options

This tap allows the following configuration variables:

* token: The name of the token to be analyzed, this is the name that appears on the url, e.g. for ETH, the url is https://www.coingecko.com/en/coins/ethereum, so the token name is `ethereum`

* start_date: The data is downloaded daily, so this is the first day to go after

* api_url: The API URL (Default is https://api.coingecko.com/api/v3)

### Source Authentication and Authorization

- [ ] `Developer TODO:` If your tap requires special access on the source system, or any special authentication requirements, provide those here.

## Usage

You can easily run `tap-coingecko` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_coingecko/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-coingecko` CLI interface directly using `poetry run`:

```bash
poetry run tap-coingecko --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-coingecko
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-coingecko --version
# OR run a test `elt` pipeline:
meltano elt tap-coingecko target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
