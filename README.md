# Data Analytics AI Agent (DAAA)

Data Analytics AI Agent (DAAA) is an intelligent analytics assistant designed to help you explore and visualize retail sales data. By leveraging LLMs (Large Language Models) like Claude or GPT-4, the system translates natural language questions into precise SQL queries, executes them against a Superstore dataset, and presents the results through interactive visual components.

## 🚀 What this system does

- **Natural Language to SQL**: Ask questions in plain English (e.g., *"What were the total sales in California last year?"*) and the AI generates the appropriate SQLite query.
- **Rich Visualizations**: Automatically renders data using interactive KPI cards, trend lines, bar charts, and detailed tables.
- **Retail Intelligence**: Specifically tuned for the "Superstore" schema, covering orders, products, customers, and regional performance.
- **Actionable Insights**: Provides suggested follow-up questions to help you dive deeper into the data.

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (must be running)
- An API Key for either [Anthropic](https://console.anthropic.com/) (Claude) or [OpenAI](https://platform.openai.com/)

## ⚙️ Setup & Execution

Follow these steps to get the system up and running:

### 1. Configure Environment Variables
Copy the example environment file to create your own configuration:
```bash
cp .env.example .env
```
Open the `.env` file and add your API keys:
- `ANTHROPIC_API_KEY`: Your Claude API key.
- `OPENAI_API_KEY`: Your OpenAI API key.

*Note: You only need one of these depending on which model you want to use (configured via `ANTHROPIC_MODEL` or `OPENAI_MODEL`).*

### 2. Start the System
Run the startup script corresponding to your operating system. This will build the Docker containers and start both the backend (Flask) and frontend (React/Vite).

- **macOS / Linux:**
  ```bash
  chmod +x start.sh
  ./start.sh
  ```
- **Windows (PowerShell):**
  ```powershell
  .\start.ps1
  ```
- **Windows (Command Prompt):**
  ```cmd
  start.bat
  ```

### 3. Access the Dashboard
Once the startup process is complete and the containers are running:
- **Frontend UI:** [http://localhost:3000](http://localhost:3000)
- **API Health Check:** [http://localhost:5000/api/health](http://localhost:5000/api/health)

## 📁 Project Structure

- `/app`: Python Flask backend containing the AI agent logic and tools.
- `/frontend`: React application for the chat interface and data visualizations.
- `/data`: Contains the SQLite database and raw CSV files.
