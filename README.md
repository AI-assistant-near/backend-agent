Money Talks Client
Navigating crypto and managing wallets on different chains is complex and tiresome. Money Talk allows you to control your assets via voice, removing the difficult barriers to crypto entry.

How it works
When first speaking to our AI voice agent, you’ll be registered as a new user and given a NEAR and Zcash account. After funding your brand new account, you can talk to the agent, which uses an LLM to parse your words to call tools provided by the agent to perform specific tasks, such as swapping NEAR for Zcash.

Swapping is happening via intents but the whole process is abstracted. The user is registered in the intents contract, wraps their near, deposits it in the intents contract, finds the best solver to make a swap, performs the swap, and withdraws it to their zcash address in all one action.

The signing for the TX happens via Liveness Proof. When the agent recognizes which tokens the user wants to swap, the agent then generates a random phrase for the user to speak, and if the agent recognizes the user (using cosine similarity comparisons with the embedding of the phrases the user spoke when registered), the agent signs the transaction on behalf of the user.

Returning users will be recognised by their voice, and their account details will automatically be loaded up for them.

All of this happens inside of a TEE on the Phala network, meaning that the whole system is running trustlessly with no third-party custody of your private keys, and you do not have to manage your own keys.

# How to run the agent

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

