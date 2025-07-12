# EMA UI [![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## Description

This project provides the User Interface for the Electric Magnitudes Analyzer tool. It is built using FastAPI and Chainlit, and leverages the Google ADK (Agent Development Kit) for agent orchestration.

Key features include:

- **User Interface:** A conversational interface built with Chainlit.
- **Agent Orchestration:** Utilizes the Google ADK Runner to manage the agent's execution flow.
- **Firebase Integration:**
  - **Session Management:** Uses Firestore to store and retrieve user session data.
  - **Artifact Storage:** Uses Firebase Storage to save and load artifacts generated or used by the agent.

### Agent and Tool Structure

The agent and tool logic is organized within the `/app/agents/` directory.

- **Main Agent:** The primary agent orchestrates the overall conversation flow and delegates tasks to specialized sub-agents.
- **Sub-agents:** Located in the `/app/agents/sub_agents/` directory, these agents are responsible for specific domains:
  - **Data Scientist Agent:** Handles tasks related to data analysis, processing, and interpretation.
  - **Electric Engineer Agent:** Focuses on tasks requiring expertise in electrical engineering concepts.
  - **Reviewer Agent:** Provides a review or evaluation function, possibly validating outputs from other agents.
- **Tools:** The `/app/agents/tools/` directory contains custom tools that agents can utilize to perform specific actions or interact with external services.
  - **Store Management Tool:** The `store_management_tool.py` file implements a RAG (Retrieval Augmented Generation) structure specifically designed to store, manage, access, and query ANEEL current regulations and the agents' learnings about them.

This modular structure allows for clear separation of concerns and facilitates the development and maintenance of specialized agent functionalities.


### Requirements

- [Python](https://python.org) **(v3.11+)**
- [PDM](https://pdm-project.org) **(v2.22+)**
- [Chainlit](https://docs.chainlit.io/get-started/overview) **(v2.5.5)**
- **Firebase Project:** A Firebase project with Authentication, Firestore, and Storage enabled.
- **Firebase Admin SDK:** Credentials for the Firebase Admin SDK to access Firestore and Storage.

## Usage

### Environment Variables

The application requires the following environment variables to be set. You can create a `.env` file in the project root and define them there.

- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID.
- `GOOGLE_CLOUD_LOCATION`: The Google Cloud location for your project (e.g., 'us-central1').
- `GOOGLE_GENAI_USE_VERTEXAI`: Set to `True` if using Vertex AI for Gemini.
- `BG_DATASET_NAME`: The name of your BigQuery dataset.
- `BG_TABLE_NAME`: The name of your BigQuery table.
- `GEMINI_API_KEY`: Your Gemini API key (if not using Vertex AI).
- `LLM_MODEL_NAME`: The name of the LLM model to use (e.g., "gemini-2.0-flash").
- `OAUTH_GOOGLE_CLIENT_ID`: Your Google OAuth client ID.
- `OAUTH_GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret.
- `CHAINLIT_AUTH_SECRET`: A secret for Chainlit authentication.
- `OAUTH_PROMPT`: OAuth prompt parameter.
- `SERVICE_NAME`: The name of your service.
- `APP_NAME`: The name of your application.
- `FIREBASE_CREDENTIALS`: JSON string of your Firebase Admin SDK service account key. **Be cautious with storing credentials directly in `.env` in production environments.** Consider more secure methods like Google Cloud Secret Manager.
- `FIREBASE_STORAGE_BUCKET`: The name of your Firebase Storage bucket (e.g., 'your-bucket-name.appspot.com' or 'gs://your-bucket-name').


### Install Dependencies

```sh
pdm install
```

### <a id="commits"/> Commits

This project uses the [Semantic Version](http://semver.org) pattern to generate the package release and it changelogs. To make it work properly, it implement a different flow of actions for commits.


```sh
pdm run commit # start the commit pipeline
```

The commit pipeline is supported by the [Commitizen](https://commitizen-tools.github.io/commitizen/) module. The first one is a cli tool that guide the devloper through the commit pipeline by inquiring for what need to be done. And the second one check if the generated commit follows the [Semantic Version](http://semver.org) pattern.
