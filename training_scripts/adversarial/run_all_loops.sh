#!/bin/bash
export PROJECT_ROOT=/home/jake/Downloads/training
export PYTHONPATH=$PROJECT_ROOT/python_env:$PYTHONPATH
VENV_PYTHON=$PROJECT_ROOT/.venv/bin/python

# Ensure logs directory exists
mkdir -p logs/loops

echo "🚀 Launching Omega Protocol: Dynamic Entropy-Driven Scheduler (DEDS v2.0)"

# 1. Start the Universal Arena and Matrix Observer as permanent continuous daemons
# (These listen to and route data rather than doing heavy batched compute)
nohup $VENV_PYTHON -u python_env/agent_zero/universal_arena.py > logs/loops/universal_arena.log 2>&1 &
nohup $VENV_PYTHON -u python_env/matrix/matrix_observer.py > logs/loops/matrix_observer.log 2>&1 &

# 2. Launch the Central Orchestrator to govern the rest of the compute nodes
# The DEDS orchestrator will run continuously in the foreground (or background if preferred).
# We run it in the background here so the script returns.
nohup $VENV_PYTHON -u python_env/deds_orchestrator.py > logs/loops/deds_orchestrator.log 2>&1 &

echo "✅ DEDS v2.0 is online. The system is now self-regulating compute based on Informational Yield."
echo "Tail logs/loops/deds_orchestrator.log to watch the logical control policy in action."
