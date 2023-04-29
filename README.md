# RED Auto-GPT
## Security Red Team Auto-GPT tool kit

We are working on creating a tool kit for security professionals that will help test network and other vulnerabilities for home and office using AutoGPT and Langchain

# ⚠️🔴 NOT TO BE USED FOR ILLEGAL ACTIVITY 🔴⚠️

## Development
We are currently working on expanding tools.


# Environment
You should create a virtualenv with the required dependencies by running
```
make virtualenv
```

Activate the virtualenv by running
```
source ./.venv/bin/activate
```

When a new requirement is needed you should add it to `unpinned_requirements.txt` and run
```
make update-requirements-txt
make virtualenv
```
this ensure that all requirements are pinned and work together for ensuring reproducibility

## Make a copy of the example environment variables file
```
cp .env.template .env
```

# Run the app
```
streamlit run chatbot.py | tail -n +6 > tools/logs/logtest04292023.txt 
```
