# EyeCode

<img src="https://github.com/user-attachments/assets/0c07d891-c0d2-4680-9b41-a683c17c39ee" alt="EyeCode Logo" width="180" />

## Inspiration

Coding can be extremely challenging and tedious for visually impaired or physically disabled developers, who often struggle with complex visual syntax, manual typing, and slow screen readers. EyeCode bridges the gap between human speech and programming, creating a tool that allows developers to write and execute code completely hands-free using just their voice.

## What it does

EyeCode is a voice-powered multi-language code generator and execution assistant specifically designed to empower visually impaired and physically disabled developers. Users can simply speak out what they want to code in their preferred language, and the application instantly converts it into clean, executable code using advanced artificial intelligence via the **Groq API**. Furthermore, users can select from multiple programming languages, including **Python**, **JavaScript**, **C++**, **Java**, **Go**, **Rust** and another languages, then run the code directly in the browser with real-time output powered by the **Judge0 API**.

## How I built it

The project architecture is built around a modern, high-performance tech stack designed for speed, security, and responsiveness:

* Backend: Powered by **Python** and **FastAPI** to efficiently handle API requests, asynchronous operations, and routing.
* AI Integration: Integrated with the **Groq API** leveraging ultra-fast large language models to deliver accurate voice-to-text transcription and intelligent code generation.
* Code Execution: Utilizes the **Judge0 API** to provide a secure, sandboxed environment for remote code compilation and execution across multiple programming languages.
* Frontend: Developed using **HTML5, CSS3, JavaScript,** and **Bootstrap** to ensure a clean, modern, and fully responsive user interface.

## Challenges I ran into
- Handling various programming language syntaxes dynamically and feeding them to remote compilers without server-side crashes.
- Managing **API latency** and ensuring smooth, asynchronous communication between the voice recorder, LLM, and the code runner.

## Accomplishments that I'm proud of
- Successfully integrating **multi-language support** so developers are not limited to just Python.
- Creating a seamless, user-friendly **speech-to-code workflow** that actually works in real-time.

## What's next for EyeCode
- Developing and releasing an official **VS Code Extension** to bring voice-powered coding directly inside the developer's favorite IDE.
- Adding advanced accessibility features, including specialized capabilities and extended support for visually impaired developers.
- To convert and adapt other programming tools so that visually impaired developers can work without any difficulties.