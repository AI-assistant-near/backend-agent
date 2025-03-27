# Python Execution Guide

This guide explains how to set up and execute the Python application without using the TEE simulator.

## Prerequisites

- Python version **3.11** installed
- At least **15GB** of free disk space

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-repo/your-project.git
   cd your-project
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Run the Python application with:

```bash
python run.py
```

## Notes

- Ensure that all dependencies in `requirements.txt` are installed before running the script.
- If running on Windows, use `python` instead of `python3.11` where necessary.

# Python TEE Simulator Template

Now, to use the application inside TEE Simulator, follow the steps bellow.

## Getting Started

1. Run the TEE Remote Attestation Simulator:

```bash
docker run --rm -p 8090:8090 phalanetwork/tappd-simulator:latest
```

2. Build the python docker container:

```bash
docker build -t your-dapp:latest .
```

3. Run the docker container:

```bash
docker run --rm -p 3000:3000 your-dapp:latest
```

