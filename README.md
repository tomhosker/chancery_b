# His Majesty's Chancery: Formulary B

## About

The code in this repository constitutes **Formulary B** of **His Majesty's Chancery**, which concerns the drawing up of **Royal Warrants**.

In addition to compiling the PDF for each warrant, the code in this repository also allows for:

* Affixing a **digital stamp** to each warrant.
    * Creating a **public** and **private key** for the above de novo.
* Entering each warrant into a blockchain ledger.

## Getting Started

### Installation

Note that the code in this repository is intended to run a **Linux** machine.

To install Formulary B:

1. Download a copy of this repository onto your computer.
1. From the command line, navigate to that copy.
1. Run `pip install .`.
1. Run `python3 install_specials.py`.

### Generating Keys

If you need to generate new **public** and **private keys**, simply run:

```sh
    generate-chancery-keys
```

You will be prompted in due course for a password with which to use the private key.

## Usage

### Create and Upload a New Warrant

1. Prepare an ordinance inputs JSON file. (See `example_input_files` for guidance.)
1. Run `upload-ordinance path/to/inputs.json`.

You will be prompted for a password with which to use the private key.

### Extract a Warrant

To extract a warrant, i.e. to convert a record from the ledger into a PDF, plus annexe(s):

1. Open the ledger; the default path is `~/chancery_b_data/ledger.db`.
1. Find the ordinal of the warrant you wish to extract.
1. To extract, say, the warrant whose ordinal is 1, run `extract-ordinance 1`.

The extract can then be found in the `extracts` folder, which should be in the same directory as the ledger.

### Verify a Warrant

Simply run:

```sh
    verify-ordinance-pdf path/to/warrant.pdf
```
