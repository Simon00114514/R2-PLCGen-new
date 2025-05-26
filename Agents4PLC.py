# -*- coding: utf-8 -*-
import subprocess
scripts = [
    'Agents4PLC/Agent4PLC_Planner.py',
    'Agents4PLC/Agents4PLC_coder.py',
    'Agents4PLC/Agents4PLC_Debugger.py',
]

# 按顺序运行每个脚本
for script in scripts:
    print(f'Running {script}...')
    result = subprocess.run(['python', script], check=True)
    print(f'{script} completed with return code {result.returncode}.')
