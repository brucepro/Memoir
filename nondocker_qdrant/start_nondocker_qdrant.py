import subprocess
import threading
import atexit
import os
import signal


current_dir: str = os.path.dirname(os.path.abspath(__file__))


def terminate_qdrant_server(process):
    if process.poll() is None:  # Check if the process is still running
        os.kill(process.pid, signal.SIGTERM)  # Send termination signal
        process.wait()  # Wait for the process to terminate


def start_qdrant_server():
    # Define the path to the qdrant executable and configuration file
    qdrant_executable: str = os.path.join(current_dir, "qdrant.exe")
    config_file: str = os.path.join(current_dir, "nondocker_qdrant_config.yaml")

    if not os.path.isfile(qdrant_executable):
        raise FileNotFoundError(f"Failed to find 'qdrant.exe' at {qdrant_executable}")

    if not os.path.isfile(config_file):
        raise FileNotFoundError(f"Failed to find 'nondocker_qdrant_config.yaml' at {config_file}")

    print(f"qdrant.exe at {qdrant_executable}\nconfig file at {config_file}\n")

    # Start the Qdrant server as a background process
    with open(os.devnull, "wb") as devnull:
        process = subprocess.Popen(
            [qdrant_executable, '--config-path', config_file],
            stdout=devnull,
            stderr=devnull
        )

    # Register a cleanup function to terminate the server on program exit
    atexit.register(terminate_qdrant_server, process)

    return process
