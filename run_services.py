#!/usr/bin/env python3
import sys
import os
import subprocess
import time
import signal
import threading

# Color codes for clean output
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

processes = {}

def log_output(prefix, color, stream):
    """Streams stdout/stderr of a process prefixed with service identity."""
    for line in iter(stream.readline, b''):
        decoded_line = line.decode('utf-8', errors='ignore').rstrip()
        if decoded_line:
            print(f"{color}[{prefix}]{RESET} {decoded_line}")
    stream.close()

def shutdown_handler(signum, frame):
    """Handles SIGINT/SIGTERM, terminating all spawned subprocesses cleanly."""
    print(f"\n{RED}{BOLD}[System] Shutdown signal received. Terminating all microservices...{RESET}")
    for name, proc in processes.items():
        if proc.poll() is None:
            print(f"{YELLOW}[System] Stopping {name} (PID: {proc.pid})...{RESET}")
            proc.terminate()
    
    # Wait for processes to stop
    time.sleep(1)
    for name, proc in processes.items():
        if proc.poll() is None:
            print(f"{RED}[System] Killing {name} (PID: {proc.pid}) forcefully...{RESET}")
            proc.kill()
            
    print(f"{GREEN}{BOLD}[System] All microservices terminated successfully. Goodbye!{RESET}")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

def main():
    print(f"{BLUE}{BOLD}===================================================================={RESET}")
    print(f"{BLUE}{BOLD}                    LAWEDAI SERVICES MASTER BOOTUP                 {RESET}")
    print(f"{BLUE}{BOLD}===================================================================={RESET}")
    # Determine the best python executable (prioritize local virtual environment if it exists)
    local_venv_python = os.path.join(os.getcwd(), ".venv", "bin", "python")
    if not os.path.exists(local_venv_python):
        # Support Windows pathing just in case
        local_venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
        
    python_exe = sys.executable
    if os.path.exists(local_venv_python):
        python_exe = local_venv_python
        print(f"[System] Virtual environment detected. Using local Python: {python_exe}")
    else:
        print(f"[System] Virtual environment NOT detected at {os.path.join(os.getcwd(), '.venv')}. Falling back to: {python_exe}")
        
    print(f"[System] Root directory: {os.getcwd()}")
    
    # List of microservices to launch
    services_config = [
        {
            "name": "Auth Service",
            "module": "backend.services.auth.main:app",
            "port": "8001",
            "color": YELLOW
        },
        {
            "name": "RAG Service",
            "module": "backend.services.rag.main:app",
            "port": "8002",
            "color": CYAN
        },
        {
            "name": "Courtroom Service",
            "module": "backend.services.courtroom.main:app",
            "port": "8003",
            "color": GREEN
        },
        {
            "name": "Gateway Service",
            "module": "backend.services.gateway.main:app",
            "port": "8000",
            "color": BLUE
        }
    ]

    # Set PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    # Launch each service
    for service in services_config:
        name = service["name"]
        module = service["module"]
        port = service["port"]
        color = service["color"]

        cmd = [
            python_exe, "-m", "uvicorn", module,
            "--host", "0.0.0.0",
            "--port", port
        ]
        
        print(f"[System] Launching {name} on port {port}...")
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            processes[name] = proc
            
            # Start threads to read stdout and stderr
            t_out = threading.Thread(target=log_output, args=(name, color, proc.stdout), daemon=True)
            t_err = threading.Thread(target=log_output, args=(name, color, proc.stderr), daemon=True)
            t_out.start()
            t_err.start()
            
            # Brief delay to allow startup before starting the next service
            time.sleep(1.0)
        except Exception as e:
            print(f"{RED}[System] Failed to launch {name}: {e}{RESET}")
            shutdown_handler(None, None)

    print(f"\n{GREEN}{BOLD}[System] All microservices are active!{RESET}")
    print(f"[System] API Gateway & Frontend: {GREEN}{BOLD}http://localhost:8000{RESET}")
    print(f"[System] Press Ctrl+C to terminate all services.\n")

    # Monitor processes and keep main thread alive
    try:
        while True:
            for name, proc in list(processes.items()):
                status = proc.poll()
                if status is not None:
                    print(f"{RED}[System] {name} has stopped unexpectedly with code {status}.{RESET}")
                    shutdown_handler(None, None)
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown_handler(None, None)

if __name__ == "__main__":
    main()
