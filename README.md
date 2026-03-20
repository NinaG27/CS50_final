### AI assistent for learning French  
A full-stack web application that helps users learn French through an AI-powered assistant, with support for conversation history, note-taking, and personalized practice. 
It was created as a final project for the Harvards CS50 course also as an opertunity to learn more Python. 

### Features

**Login and Registration** 
- User registration and login system.
- Secure session handling for personilased experiance.

**AI-powered chat** 
- Interactive chatbot designed to assist with French learning.  
- The responses are generated via Groq API integration. 

**Note system** 

- Users are add, edit and delete notes taken from lessions. 

**History page** 

- Persistant chat history organised by date. 

### Tech Stack

**Backend**: Python, Flask
**Frontend**: HTML, CSS, JavaScript
**Database**: SQLite
**AI Integration**: Groq API

### Learning Outcomes

This project was a great opportunity to apply the skills learned in the course, as well as explore additional topics such as:

- How the backend communicates with both the database and the frontend
- Designing and creating databases 
- API route design
- Planning and building a full-stack application
- The limitations and advantages of using AI assistance
- The strengths of the Python ecosystem and its libraries (SQLAlchemy) 
- Gaining deeper experience with Flask

### Future Improvements

Some further learning opertunities that would translate well into features: 

**Context aware ai** I really want to give the assistant memory and deeper context. I’ve been exploring different database options (such as vector databases) to support this. Using a different model may also improve performance.

**Frontend rewrite** I wanted to challange myself to rewrite some of the logic on the frontend to use React and Typscript insted of JavaScript in the future. 

----------------------------------

To run this project localy you will need Groq api key. You can get one for free by registaring at: [https://groq.com](https://groq.com): 

**1. Create environment variables**
Add .env file to the root project directory and add: 

`GROQ_API_KEY=<add your key here> 
SECRET_KEY=dev`

**2. Install and run**

`python3 -m venv .venv`
`pip install -r requirements.txt`
`flask --app flaskr run`

This runs the app in the development mode.
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.
  
