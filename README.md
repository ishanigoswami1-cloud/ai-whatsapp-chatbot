# 🤖 AI WhatsApp Chatbot for Domestic RO & Water Purifier

An AI-powered chatbot designed for **domestic RO and water purifier businesses**. It helps customers understand their requirements, recommends suitable products, handles conversations, maintains memory, and supports lead generation.

The project combines AI-powered conversations with product recommendations, customer information extraction, conversation memory, and lead management.

## 🚀 Features

* 🤖 AI-powered customer conversations
* 💧 Domestic RO & water purifier product recommendations
* 🧠 Conversation memory
* 📋 Customer information extraction
* 🎯 Lead generation and lead handling
* 💬 Interactive chatbot experience
* 🛒 Requirement-based product suggestions
* 📝 Custom AI prompts
* ⚡ Python-based backend
* 🔄 Modular chatbot architecture

## 🎯 Project Objective

The main goal of this project is to automate the initial **sales and customer assistance process** for domestic RO and water purifier businesses.

Instead of manually answering every customer query, the AI chatbot can:

1. Understand the customer's requirement.
2. Ask relevant questions.
3. Analyze the customer's needs.
4. Recommend suitable RO/water purifier products.
5. Extract important customer information.
6. Maintain conversation context.
7. Generate and manage potential leads.

## 🏗️ Project Architecture

```text
                    Customer
                       │
                       ▼
                ┌─────────────┐
                │   app.py    │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │ chatbot.py  │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │  prompt.py  │
                │ AI Prompts  │
                └──────┬──────┘
                       │
                       ▼
                  AI / LLM
                       │
            ┌──────────┼──────────┐
            │          │          │
            ▼          ▼          ▼
       memory.py  product.py  exractor.py
            │          │          │
            │          │          ▼
            │          │    Customer Details
            │          │
            │          ▼
            │    Product Recommendation
            │
            ▼
       Conversation Memory
                       │
                       ▼
                   lead.py
                       │
                       ▼
                Lead Generation
```

## 📁 Project Structure

```text
ai-whatsapp-chatbot/
│
├── .gitignore
├── app.py
├── chatbot.py
├── exractor.py
├── lead.py
├── memory.py
├── product.py
├── prompt.py
├── requirements.txt
├── run.py
└── README.md
```

## 📌 File Overview

| File               | Description                                                   |
| ------------------ | ------------------------------------------------------------- |
| `app.py`           | Main application logic and application interface              |
| `chatbot.py`       | Handles chatbot conversation and AI interaction               |
| `exractor.py`      | Extracts relevant customer information from conversations     |
| `lead.py`          | Handles lead-related information and lead generation          |
| `memory.py`        | Maintains conversation context and memory                     |
| `product.py`       | Handles product information and recommendations               |
| `prompt.py`        | Contains AI prompts and chatbot instructions                  |
| `run.py`           | Starts/runs the application                                   |
| `requirements.txt` | Contains required Python dependencies                         |
| `.gitignore`       | Prevents sensitive and unnecessary files from being committed |

## 💧 How the Chatbot Works

The chatbot follows a customer-focused sales flow.

### Example

```text
Customer:
"I need an RO for my home."

        ↓

AI Chatbot:
Understands the requirement

        ↓

AI Chatbot:
Asks about water source,
family size, budget, etc.

        ↓

Customer:
"Borewell water, 5 members."

        ↓

Product Recommendation:
Suggests suitable RO/water purifier options

        ↓

Information Extraction:
Extracts relevant customer details

        ↓

Lead Management:
Stores/processes potential customer lead
```

## 🧠 Conversation Memory

The chatbot is designed to maintain conversation context so that customers do not need to repeat information already provided during the conversation.

Memory helps the chatbot:

* Remember previous messages
* Maintain context
* Understand customer requirements
* Provide more relevant responses
* Continue conversations naturally

## 🛒 Product Recommendation

The chatbot can use customer requirements to recommend suitable domestic RO/water purifier products.

Possible factors include:

* Water source
* Water quality
* Number of family members
* Budget
* Purification requirements
* Product preferences

This makes the chatbot useful as an **AI-powered sales assistant** rather than only a basic question-answering bot.

## 📋 Lead Generation

The chatbot can identify important information from customer conversations and use it to support lead generation.

Potential lead information can include:

* Customer name
* Contact details
* Location
* Water source
* Family size
* Product requirement
* Budget
* Purchase intent

## 🛠️ Tech Stack

* **Python**
* **AI / LLM**
* **Chatbot Automation**
* **Conversation Memory**
* **Product Recommendation**
* **Lead Generation**
* **API / Backend Integration**

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-whatsapp-chatbot.git
cd ai-whatsapp-chatbot
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

If the project requires API keys or other credentials, create a `.env` file and add the required values.

**Never upload real API keys, passwords, tokens, or other secrets to GitHub.**

### 5. Run the application

```bash
python run.py
```

If the project is configured to run through the application server, use the appropriate command defined in the project configuration.

## 🔐 Security

Sensitive information should never be committed to the repository.

The `.gitignore` file should exclude files such as:

```text
.env
venv/
.venv/
__pycache__/
*.pyc
```

## 🎯 Use Cases

This chatbot architecture can be adapted for:

* Domestic RO sales
* Water purifier sales
* Customer support
* Product recommendations
* Lead generation
* Lead qualification
* Customer requirement collection
* Sales automation
* Business inquiry handling

## 🔮 Future Improvements

Possible future improvements include:

* WhatsApp API integration
* CRM integration
* Automated follow-ups
* Lead scoring
* Product catalog integration
* Customer analytics dashboard
* Advanced AI agent workflows
* Automated appointment/demo booking
* Multiple specialized AI agents

## 👩‍💻 Author

**Pinki Giri**

AI & Python Developer

Interested in **AI Agents, AI Chatbots, Python, FastAPI, Automation, API Integrations, and Local SEO Automation**.
