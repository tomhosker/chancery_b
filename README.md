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

1. Download a copy of this repository into the home directory of your computer.
1. From the command line, navigate to that copy.
1. Run `sh install_externals`.

### Create and Upload a New Warrant

1. Update ordinance_inputs.py and annexe/ as required.
1. Run `sh upload_ordinance`.

### Extract a Warrant

To extract a warrant, i.e. to convert a record from the ledger into a PDF, plus annexe(s):

1. Open ledger.db.
1. Find the ordinal of the warrant you wish to extract.
1. To extract, say, the warrant whose ordinal is 1, run `sh extract_ordinance 1`.

The extract can then be found in extracts/ in the subdirectory named for the ordinal of the warrant in question.
