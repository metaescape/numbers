Codes about numbers, logic, and computation.

## python requirements

python3.8 or later

## `analysis/`

contains the codes for Chapters 2, 4, and 5 of the book "Analysis" by Terence Tao.

## `turing_machine/`

contains the code for Turing's 1936 paper.

To run the tests for the Turing machine:

- Use `make test-machine`.

To run the tests for the abbreviated table (a high-level language for Turing machines):

- Use `make test-abb`.

To run the tests for the encoding of Turing machines:

- Use `make test-encode`.

To run the tests for the universal Turing machine:

- Use `make test-uni`.

Alternatively, you can manually run the commands in the Makefile.

To run the tests for the reduction of the halting problem:

- Use `make test-reduce`.

## `lambda/`

interpreter for lambda calculus and combinatory logic.

To run the tests for the lambda calculus:

```bash
cd lambda
python rewriter.py
```
