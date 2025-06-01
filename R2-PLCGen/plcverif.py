#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Beremiz ... (keeping original license headers for context)
# ... (rest of the license headers) ...

import os
import sys
import subprocess  # Preferred over os.system


# Removed wx, wx.html2, wx.grid, xml_translate imports as they are GUI related
# If xml_translate was a non-GUI utility function potentially needed, it could be kept.
# For now, assuming it was tied to the GUI button.

def parse_cli_set(filepath):
    config = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and comments
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove surrounding quotes if present (e.g., "value" -> value)
                    if (value.startswith('"') and value.endswith('"')) or \
                            (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    config[key] = value
    except FileNotFoundError:
        print(f"Error: Configuration file {filepath} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing configuration file {filepath}: {e}")
        sys.exit(1)
    return config


def run_verification():
    """
    Runs the verification process based on cli_set.txt.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct paths relative to the script's location
    # PLCverif_cli directory is expected to be your own path
    plcverif_cli_dir = "D:\\project\\R2-PLCGen\\R2-PLCGen\\PLCverif_cli"
    plcverif_executable = os.path.join(plcverif_cli_dir, "eclipsec.exe")
    cli_settings_file = os.path.join(plcverif_cli_dir, "cli_set.txt")

    # Check if essential files/dirs exist
    if not os.path.isdir(plcverif_cli_dir):
        print(f"Error: PLCverif_cli directory not found at {plcverif_cli_dir}")
        print(f"Ensure it's a subdirectory relative to the script: {current_dir}")
        sys.exit(1)
    if not os.path.isfile(plcverif_executable):
        print(f"Error: Verifier executable not found at {plcverif_executable}")
        sys.exit(1)
    if not os.path.isfile(cli_settings_file):
        print(f"Error: Settings file not found at {cli_settings_file}")
        sys.exit(1)

    # Parse cli_set.txt to get necessary info, e.g., for report path
    config = parse_cli_set(cli_settings_file)

    verification_id = config.get("-id")
    if not verification_id:
        print("Error: '-id' not found in cli_set.txt. This is needed for the report filename.")
        sys.exit(1)

    # Determine the output directory for the report
    # The original script hardcoded part of this. Let's try to be consistent.
    # cli_set.txt has "-output = PLCverif_cli/output".
    # If eclipsec.exe CWD is plcverif_cli_dir, then relative path "output" is sufficient in cli_set.txt.
    # The report path constructed by the original script was:
    # html_file_dir = os.path.join(current_dir, "PLCverif_cli", "output")
    # report_filename = self.id_text.GetValue() + '.report.html'
    # self.html_file_path = os.path.join(html_file_dir, report_filename)

    # Let's assume the output directory specified in cli_set.txt (-output) is relative
    # to the plcverif_cli_dir (which will be the CWD for eclipsec.exe).
    # If cli_set.txt says "-output = output", then reports go to "plcverif_cli_dir/output/".
    # If cli_set.txt says "-output = PLCverif_cli/output", and CWD is plcverif_cli_dir,
    # this could lead to "plcverif_cli_dir/PLCverif_cli/output".
    # For robust report path prediction, it's best if cli_set.txt's -output is simple like "output".

    # The python script will predict the report path based on original logic:
    # current_dir/PLCverif_cli/output/ID.report.html
    expected_report_output_dir = os.path.join(plcverif_cli_dir, "output")  # This is where this script expects it

    # Ensure this expected output directory by Python script exists
    # eclipsec.exe should ideally create its output directory based on its own config.
    os.makedirs(expected_report_output_dir, exist_ok=True)

    html_report_path = os.path.join(expected_report_output_dir, f"{verification_id}.report.html")

    # --- Construct the command for eclipsec.exe ---
    # The eclipsec.exe tool is given the cli_set.txt file as its main configuration.
    # All specific parameters (ID, name, sourcefiles, pattern, etc.) should be read by
    # eclipsec.exe directly from the cli_set.txt file.
    command = [plcverif_executable, cli_settings_file]

    print(f"Starting verification...")
    print(f"Executing: \"{plcverif_executable}\" \"{cli_settings_file}\"")
    print(f"Working directory for eclipsec.exe will be: {plcverif_cli_dir}")

    try:
        # Run eclipsec.exe. It's important to set the CWD (Current Working Directory)
        # to plcverif_cli_dir because cli_set.txt might contain relative paths
        # (e.g., "./NuSMV.exe", "output" for -output) that are relative to that directory.
        process = subprocess.run(
            command,
            cwd=plcverif_cli_dir,  # Set working directory
            check=True,  # Raise an exception for non-zero exit codes
            capture_output=True,  # Capture stdout and stderr
            text=True,  # Decode output as text
            encoding='utf-8',  # Specify encoding
            errors='replace'  # Handle potential decoding errors
        )
        print("\n--- eclipsec.exe STDOUT ---")
        print(process.stdout)
        if process.stderr:
            print("\n--- eclipsec.exe STDERR ---")  # NuSMV often prints to stderr
            print(process.stderr)
        print("Verification process completed successfully.")

    except subprocess.CalledProcessError as e:
        print("\n--- eclipsec.exe STDOUT (on error) ---")
        print(e.stdout)
        print("\n--- eclipsec.exe STDERR (on error) ---")
        print(e.stderr)
        print(f"Verification failed with exit code {e.returncode}.")
        sys.exit(1)
    except FileNotFoundError:
        # This would catch if plcverif_executable itself is not found by subprocess
        print(f"Error: Command '{plcverif_executable}' not found. Ensure it's correctly specified and executable.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during verification: {e}")
        sys.exit(1)

    print(f"\nVerification finished.")
    # Check if the report was generated where this script expects it.
    # Note: eclipsec.exe will place the report based on its own interpretation of the -output
    # setting in cli_set.txt, relative to its CWD (which we set to plcverif_cli_dir).
    # If cli_set.txt has `-output = output`, the report will be in `plcverif_cli_dir/output/`.
    if os.path.exists(html_report_path):
        print(f"Report is expected at: {html_report_path}")
    else:
        print(f"Report was expected at: {html_report_path} (BUT NOT FOUND!)")
        print("Please check:")
        print(f"1. The eclipsec.exe output above for any errors or alternative report location.")
        print(
            f"2. The '-output' setting in '{cli_settings_file}'. Currently it is: '{config.get('-output', 'Not Set')}'")
        print(f"   If CWD for eclipsec.exe is '{plcverif_cli_dir}', then for the report to be at the expected path,")
        print(f"   '-output' should ideally be 'output' or './output' in '{cli_settings_file}'.")


if __name__ == "__main__":
    run_verification()