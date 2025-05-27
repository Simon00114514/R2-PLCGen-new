# R2-PLCGen: PLC Generation via Requirements Refinement and Consistency Checking

This repository contains the official implementation for the paper "R2-PLCGen: PLC Generation via Requirements Refinement and Consistency Checking". R2-PLCGen is an automated framework designed to bridge the semantic gap between abstract original requirements and final Structured Text (ST) code for Programmable Logic Controllers (PLCs) through systematic requirement refinement and rigorous consistency checking.

## Overview

R2-PLCGen employs a multi-agent, LLM-powered approach that involves:

1.  **Requirement Refinement:** Iteratively refining original requirements into detailed use cases and verifiable formal properties (CTL/LTL), guided by semantic consistency checking feedback. This involves agents like `UseCase_Agent`, `Pattern_Agent`, `Property_Agent`, `SMV_Agent`, and `Req_Agent`.
2.  **Code Generation:** Synthesizing reliable ST code from the validated refined requirements using a 'PLC Self-Healing Pipeline', involving `Code_Agent` and `Debug_Agent`.

Key innovations include the Pattern-Driven formal property generation method and a robust iterative loop for ensuring semantic fidelity at both requirement and code levels.

## Features

*   Automated refinement of abstract PLC requirements.
*   Pattern-Driven translation of use cases to formal (CTL/LTL) properties.
*   Semantic consistency checking using formal verification tools (e.g., nuXmv).
*   Iterative PLC code generation and self-healing pipeline.
*   Multi-agent framework leveraging Large Language Models (LLMs).

## Preperations

*   Python 3.9+ (or your specific recommended version)
*   Access to an LLM API (e.g., OpenAI GPT-3.5/4, or other models compatible with your agent setup). You will need to configure your API keys.
*   **PLCVerif:** This tool is used for the formal verification of generated PLC code, including syntax checking.
    *   **Installation:** Please follow the official installation instructions for PLCVerif available at: `https://gitlab.com/plcverif-oss/plcverif-docs`
    *   Ensure that PLCVerif (and its dependencies, such as a specific compiler like TIA Portal for certain checks, if required by PLCVerif itself) is correctly installed and accessible in your system's PATH or configured as per its documentation.
*   **nuXmv Model Checker:** (or nuSMV). Used for semantic consistency checking of requirements.
    *   **Installation:** Download from [http://nuxmv.fbk.eu/download.html](http://nuxmv.fbk.eu/download.html).
    *   Ensure it's installed and accessible in your system's PATH.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Simon00114514/R2-PLCGen-new.git
   cd R2-PLCGen
   ```

2. **Create a dedicated virtual environment (recommended):**
   We recommend creating a virtual environment to manage project-specific dependencies. You can name it, for example, `R2PLCGen_env`.

   * **Using `venv` (Python's built-in module):**

     ```bash
     python3 -m venv R2PLCGen_env 
     ```

     (Note: Use `python` instead of `python3` if `python3` is not your default Python 3 interpreter command, or specify your target Python version if `venv` supports it directly, e.g., `python3.9 -m venv R2PLCGen_env`)

   * **Alternatively, using `conda` (if you prefer Anaconda/Miniconda):**

     ```bash
     conda create -n R2PLCGen_env python=3.9+  
     ```

3. **Activate the virtual environment:**

   * **If you used `venv`:**

     * On macOS and Linux:

       ```bash
       source R2PLCGen_env/bin/activate
       ```

     * On Windows (Command Prompt):

       ```bash
       R2PLCGen_env\Scripts\activate.bat
       ```

     * On Windows (PowerShell):

       ```bash
       R2PLCGen_env\Scripts\Activate.ps1
       ```

       (For PowerShell, if you encounter issues, you might need to set the execution policy for the current process: `Set-ExecutionPolicy Unrestricted -Scope Process`)

   * **If you used `conda`:**

     ```bash
     conda activate R2PLCGen_env
     ```

4. **Install dependencies:**
   Once the virtual environment is activated, install the required Python packages listed in `requirements.txt`.

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up LLM API Key(s):**
   You need to provide your LLM API key(s) for the agents to function. This is typically done by setting environment variables. For example, for OpenAI:

   ```bash
   export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
   ```

   *(If your application uses a different method, like a `.env` file or a configuration script, please provide those specific instructions here. For example: "Copy `config.example.yaml` to `config.yaml` and fill in your API keys.")*

6. **Verify External Tool Installations:**

   *   **nuXmv:** Open a terminal and type `nuXmv -h`. This should display the help message.
   *   **PLCVerif:** Test its installation according to its documentation. For example, `plcverif --version` (if such a command exists).

## Usage

The main workflow of R2-PLCGen is executed through the `R2-PLCGen.py` script.

### Running the Full R2-PLCGen Workflow

To run the complete R2-PLCGen pipeline (requirement refinement followed by code generation) on a set of input requirements:

```bash
python R2-PLCGen.py 

### Running the Baseline Workflow
Individual Pipeline Components (LLM4PLC.py, Agents4PLC.py)
The files LLM4PLC.py and Agents4PLC.py are provided primarily as implementations of baseline methods for comparison, as discussed in the paper. They may have their own specific command-line arguments and operational modes.
```bash
python LLM4PLC.py
```bash
python Agents4PLC.py

```
```bash
R2-PLCGen_Root_Directory/
├── R2-PLCGen.py                # Main executable script for R2-PLCGen workflow
├── LLM4PLC.py                  # Main executable script for LLM4PLC baseline
├── Agents4PLC.py               # Main executable script for Agents4PLC baseline
├── requirements.txt            # Python dependencies
├── R2-PLCGen/                  # Core implementation of the R2-PLCGen workflow
│   ├── Code_Agent.py
│   ├── Debug_Agent.py
│   ├── Pattern_Agent.py
│   ├── Property_Agent.py
│   ├── Req_Agent.py
│   ├── SMV_Agent.py
│   ├── UseCase_Agent.py
│   ├── config.py               # Configuration for R2-PLCGen
│   ├── nuXmv.py                # Interface for nuXmv
│   └── plcverif.py             # Interface for PLCVerif
├── LLM4PLC/                    # Resources/modules for the LLM4PLC workflow
├── Agents4PLC/                 # Resources/modules for the Agents4PLC workflow
└── README.md
```
