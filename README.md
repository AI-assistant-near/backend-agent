## Money Talk: Voice-Controlled Crypto

Navigating crypto and managing wallets across multiple blockchains is often complex and frustrating. Money Talk removes these barriers by letting you control your assets using just your voice. No wallets to configure. No private keys to manage. Just speak.

⸻

## 🧠 How It Works

When you log in and first speak to our AI voice agent, you’re automatically registered as a new user and provided with NEAR and Zcash accounts.

Once your account is funded, you can interact with the agent naturally — just tell it what you want to do. An LLM (Large Language Model) parses your voice input and maps it to the appropriate tools and actions, such as swapping NEAR for Zcash.

⸻

## 🔁 Swapping, Abstracted

Swaps are powered by intents, but the process is fully abstracted for the user. Under the hood, the system:
	1.	Registers the user in the intents contract
	2.	Wraps their NEAR tokens
	3.	Deposits them into the intents contract
	4.	Finds the best-priced solver to execute the swap
	5.	Performs the swap
	6.	Withdraws the resulting assets to the user’s Zcash address

All of that happens in a single, seamless action.

⸻

## 🔐 Secure Signing via Liveness Proof

When the user requests a transaction (e.g. a swap), the agent:
	1.	Generates a random phrase for the user to speak
	2.	Compares the spoken phrase’s voice embedding to those recorded at registration using cosine similarity
	3.	If the voice matches, it signs the transaction on the user’s behalf

This is called liveness proof — a secure, biometric-based signing mechanism.

⸻

## 🔁 Seamless Experience for Returning Users

Returning users are automatically recognized by their voice. Their account data is securely loaded without the need for logins or passwords.

⸻

## 🛡️ Trustless by Design — Powered by Phala

All computation and signing occurs inside a Trusted Execution Environment (TEE) on the Phala Network. Your private keys are never exposed — even we can’t see them. The system is fully trustless, and you never have to manage your own keys.

⸻

## 🧪 Feedback & Observations
	•	It would be valuable to have an explorer for intents, allowing deeper insight into swap results and status.
	•	Zcash integration posed some friction — due to the need to run a full node for even simple operations.
 

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

