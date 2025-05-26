# -*- coding: utf-8 -*-
import subprocess
# LLM4PLC revision 2.0
scripts = [
    'LLM4PLC/LLM4PLC_Plan.py',
    'LLM4PLC/LLM4PLC_Code.py',
]

# Execute the Scripts sequentially...
for script in scripts:
    print(f'Running {script}...')
    result = subprocess.run(['python', script], check=True)
    print(f'{script} completed with return code {result.returncode}.')
    print('-' * 80)
    print('\n')
