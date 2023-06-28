# What is FuzzDriverGPT?

`fuzzdrivergpt` is a GPT-based fuzz driver generator.
It is a tool aims to generate effective fuzz drivers for guys who want to fuzz some library APIs.
Ideally, an effective fuzz driver is a piece of high quality API usage code which can sufficiently test the given APIs without raising any false positive (bugs caused by the driver code).

Currently, `fuzzdrivergpt`:
- generates prompts utilizing multiple sources of API usage knowledge
- can validate the effectiveness of the generated fuzz drivers
- can iteratively fix/improve the generated drivers

`fuzzdrivergpt` has been tested on 86 APIs collected from 30 C projects of oss-fuzz. It shows promising results: it can generate correct fuzz drivers for 55 (64%) APIs fully automatically and 23 more APIs (91%) with manually configured semantic correctness checkers for filtering out the generated drivers.

## Demo

The following demo shows the process of using iterative query strategy to generate valid fuzz drivers for `md_html` from project `md4c`.
`fuzzdrivergpt` generated a fuzz driver with compilation error in the first iteration, then it fixed that error in the following iteration using code fix prompts.

![video demo](doc/demo/demo.svg)

## Examples of generated fuzz drivers

[`examples`](https://github.com/occia/fuzzdrivergpt/tree/main/examples) provide some `fuzzdrivergpt` generated drivers using iterative query strategies.


# Usage Guidance

## Prerequisites

- python 3, [python 3.8 is recommended](https://docs.python-guide.org/starting/install3/linux/)

- docker, [docker latest install steps](https://docs.docker.com/desktop/install/linux-install/)

- [openai api key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key)

- run `install-pre.sh`

```bash
bash install-pre.sh YOUR-OPENAI-KEY YOUR-OPENAI-ORGID
```

After finishing the above, use `. venv/bin/activate` to enter the python environment for running `fuzzdrivergpt`.

## Usage 

### Project Environment Preparation

Before generating, you need to prepare the analysis environment and execution environment. Currently, we provided environment for 30 OSS-Fuzz C projects. We're refining this to make the environment preparation more general and painless.

For supported projects, run the following command (we use `md4c` as an example):
```bash
python prepareOSSFuzzImage.py -t fuzzdrivergpt-env md4c
```

### Generating the Fuzz Driver

The following command generates fuzz driver for `md_html` from project `md4c` using `gpt-4-0314` model and `ITER-BA` generation strategy. It tries up to 3 rounds (`-MR 3`) to generate the valid fuzz driver. Each round a driver will first be generated and then iteratively fixed up to 20 times (`-MI 20`). Details and results of each round are saved as `test_roundX.json`.

```bash
python main.py -l c -m gpt-4-0314 -t md4c -f md_html -q ITER-BA -MI 20 -o test.json
```

In our evaluation, `ITER-BA` and `ITER-ALL` are superior generation strategies. See [technical overview](https://github.com/occia/fuzzdrivergpt/tree/main/doc/technical_overview.md) to find more detail.

### Result interpretation

All results and details of prompts, validations, and driver codes can be found in output jsons.

- Detailed doc for output json format (coming soon)
- View local websites (coming soon)

### Tested APIs

[Tested APIs](https://github.com/occia/fuzzdrivergpt/tree/main/doc/tested_apis.md) provides a list of `-t` & `-f` options for try.

# Todo

- Better usability
	- [x] log refinement
	- [ ] More documentation
	- [ ] New process/interface for API targets out of OSS-Fuzz projects
	- [ ] Automation for API usage collection
	- [ ] Refine the heavy, manual prerequisites installation process

- Greater functionalities
	- [ ] Human experts in the loop (integrating experts feedback for better generation!)
	- [ ] Driver enhance mode (not generate from scratch but from a working one!)
	- [ ] Generate fuzz driver for closed-source APIs (such as binaries, macOS/Windows SDKs!)

- More programming languages


# License

MIT License, see LICENSE.txt.


# I Want to Contribute!

Any suggestion, contribution, or discussion for `fuzzdrivergpt` is highly appreciated.

Contributors:
- [Cen Zhang](https://www.github.com/occia)
- [Mingqiang Bai](https://www.github.com/7zq12lvm-b)
