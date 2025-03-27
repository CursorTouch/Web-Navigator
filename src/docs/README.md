# **Web Agent: Automating Browser Tasks with AI**

## Overview
**Web Agent** is a state-of-the-art browser automation tool driven by advanced AI technologies. Designed for seamless navigation and task execution on the web, it intelligently interacts with dynamic web elements, performs searches, downloads files, and adapts to page changes. By leveraging cutting-edge LLMs and the Playwright framework, Web Agent simplifies complex tasks and enhances productivity.

## Demo
https://github.com/user-attachments/assets/499f248c-b160-45cc-a6a5-2819b6955aab

---

## **Key Features**

1. **AI-Driven Decision Making**  
   - Utilizes **Groq (Llama 3.3)** and **Gemini (Gemini 2.0)** LLMs for contextual understanding and task execution.
   - Smart reasoning ensures the correct action is taken based on webpage context.

2. **Interactive Element Detection**  
   - Automatically identifies clickable elements, input fields, and navigation links.
   - Utilizes screenshots, bounding boxes, and browser state capture for precise targeting.

3. **Multi-Browser Compatibility**  
   - Supports **Chromium**, **Firefox**, and **WebKit (Safari)** via Playwright for cross-platform performance.

4. **Dynamic Adaptation**  
   - Handles dynamic content changes and page layout variations.
   - Automatically recovers from errors such as misclicks or missed interactions.

5. **Enhanced Performance Options**  
   - Supports both **visual-based** interactions through screenshots and **non-visual** interactions using accessibility trees for resource-efficient automation.

---

## **How It Works**

1. **State Capture & Interaction Analysis:**  
   - Captures browser state and webpage layout, annotates interactive elements, and stores relevant data for decision-making.

2. **LLM Integration:**  
   - Processes contextual data to determine the best action for completing tasks.
   
3. **Action Execution:**  
   - Automates task execution such as navigating pages, filling forms, and downloading content.

4. **Feedback Loop:**  
   - Evaluates outcomes and refines strategy for subsequent actions.

---

## **Usage Example**

### **Task: Download a Research Paper**

```bash
python main.py "Can you download the attention is all you need paper in ARXIV from google search"
```

#### Example Output:

```plaintext
Enter your query: Can you download the attention is all you need research paper by google from arxiv using google                                                                                     
Thought: I need to find the research paper "Attention is All You Need" on arXiv, which is hosted by Google. I will start by searching on Google for the paper and then navigate to the arXiv page to download the PDF.
Action Name: GoTo Tool
Action Input: {'url': 'https://www.google.com'}
Observation: Navigated to https://www.google.com
Thought: I'm on the Google homepage. I need to type the name of the research paper into the search bar. The search bar is element 6.
Action Name: Type Tool
Action Input: {'index': 6, 'text': 'Attention is All You Need research paper arxiv'}
Observation: Pressed Enter
Thought: I have the search results. The third result, element 25, is a link to the PDF of the paper on arXiv. I will click on this link to download the PDF.
Action Name: Click Tool
Action Input: {'index': 25}
Observation: Clicked element 25
Thought: I have navigated to the arXiv page for the paper. The PDF is already displayed in the browser. I need to download the PDF. I will use the download tool to download the file. The url of the file is the current url.
Action Name: Download Tool
Action Input: {'index': 0, 'url': 'https://arxiv.org/pdf/1706.03762', 'filename': 'Attention_is_All_You_Need.pdf'}
Observation: Downloaded Attention_is_All_You_Need.pdf from https://arxiv.org/pdf/1706.03762 and saved it to D:\Personal Projects\Web-Search-Agent\downloads\Attention_is_All_You_Need.pdf
Thought: I have successfully downloaded the PDF of the "Attention is All You Need" research paper. I can now provide the final answer to the user.
Final Answer: I have downloaded the "Attention is All You Need" research paper from arXiv. The file is saved as `Attention_is_All_You_Need.pdf`.
```

---

## **Installation Guide**

### **Prerequisites**

- Python 3.8 or higher
- Playwright installed

### **Installation Steps**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Jeomon/Web-Agent.git
   cd Web-Agent
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Playwright:**

   ```bash
   playwright install
   ```

---

## **Running the Web Agent**

Execute the following command to start the agent:

```bash
python main.py "Describe your task here"
```

Example:  
```bash
python main.py "Can you download the attention is all you need research paper by google from arxiv using google"
```

---

## **Advanced Usage**

- **Enable Debugging:** Set `verbose=True` in the agent configuration for detailed logs.
- **Custom Instructions:** Modify task-specific instructions for custom workflows.

---

## **Development & Contributions**

We welcome contributions to improve Web Agent! Please feel free to fork the repository, submit issues, or create pull requests.

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

For more information about the AGPL-3.0 license, please visit: https://www.gnu.org/licenses/agpl-3.0.en.html

---

## **References**

- **[Playwright Documentation](https://playwright.dev/docs/intro)**  
- **[LangGraph Examples](https://github.com/langchain-ai/langgraph/blob/main/examples/web-navigation/web_voyager.ipynb)**  
- **[vimGPT](https://github.com/ishan0102/vimGPT)**  
- **[WebVoyager](https://github.com/MinorJerry/WebVoyager)**  

---

## **Contact**

For queries or support, please reach out via GitHub Issues.

E-mail: jeogeoalukka@gmail.com