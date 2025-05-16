<div align="center">

  <h1>🌐 Web-Agent</h1>

  <a href="https://github.com/Jeomon/Web-Agent/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </a>
  <img src="https://img.shields.io/badge/python-3.12%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/Powered%20by-Playwright-45ba63?logo=playwright&logoColor=white" alt="Powered by Playwright">
  <br>

  <a href="https://x.com/computeraiagent">
    <img src="https://img.shields.io/badge/follow-%40computeraiagent-1DA1F2?logo=twitter&style=flat" alt="Follow on Twitter">
  </a>
  <a href="https://discord.com/invite/Aue9Yj2VzS">
    <img src="https://img.shields.io/badge/Join%20on-Discord-5865F2?logo=discord&logoColor=white&style=flat" alt="Join us on Discord">
  </a>

</div>

<br>

**Web Agent** is your intelligent browsing companion, built to seamlessly navigate websites, interact with dynamic content, perform smart searches, download files, and adapt to ever-changing pages — all with minimal effort from you. Powered by advanced LLMs and the robust Playwright framework, it transforms complex web tasks into streamlined, automated workflows that boost productivity and save time.

## 🛠️Installation Guide

### **Prerequisites**

- Python 3.11 or higher
- Langgraph
- Playwright

### **Installation Steps**

**Clone the repository:**

```bash
git clone https://github.com/Jeomon/Web-Agent.git
cd Web-Agent
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Setup Playwright:**

```bash
playwright install
```

---

**Setting up the `.env` file:**

```bash
GOOGLE_API_KEY=""
```

Basic setup of the agent.

```python
from src.inference.gemini import ChatGemini
from src.agent.web import WebAgent
from dotenv import load_dotenv
import os

load_dotenv()
google_api_key=os.getenv('GOOGLE_API_KEY')

llm=ChatGemini(model='gemini-2.0-flash',api_key=google_api_key,temperature=0)
agent=WebAgent(llm=llm,verbose=True,use_vision=False)

user_query=input('Enter your query: ')
agent_response=agent.invoke(user_query)
print(agent_response.get('output'))

```

Execute the following command to start the agent:

```bash
python app.py
```

## 🎥Demos

**Prompt:** I want to know the price details of the RTX 4060 laptop gpu from varrious sellers from amazon.in

https://github.com/user-attachments/assets/c729dda9-0ecc-4b07-9113-62fddccca52f

**Prompt:** Make a twitter post about AI on X

https://github.com/user-attachments/assets/126ef697-f506-4630-9a0a-1dbbfead9f7e

**Prompt:** Can you play the trailer of GTA 6 on youtube

https://github.com/user-attachments/assets/7abde708-7fe0-46f8-96ac-16124aaf2ef4

**Prompt:** Can you go to my github account and visit the Windows MCP

https://github.com/user-attachments/assets/cb8ad60c-0609-42e3-9fb9-584ad77c4e3a

---

## 🪪License

This project is licensed under MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝Contributing

Contributions are welcome! Please see [CONTRIBUTING](CONTRIBUTING) for setup instructions and development guidelines.

---

## 📒References

- **[Playwright Documentation](https://playwright.dev/docs/intro)**  
- **[LangGraph Examples](https://github.com/langchain-ai/langgraph/blob/main/examples/web-navigation/web_voyager.ipynb)**  
- **[vimGPT](https://github.com/ishan0102/vimGPT)**  
- **[WebVoyager](https://github.com/MinorJerry/WebVoyager)**  

---

## 🤙🏾Contact

For queries or support, please reach out via GitHub Issues.

E-mail: <jeogeoalukka@gmail.com>, <yaseenap0001@gmail.com>
