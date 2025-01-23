# Dynamic AI Character: Social Media Post Simulation

## Project Overview
This project focuses on creating a dynamic AI character capable of generating daily social media posts. The character has a unique personality, behaviors, and routines that mimic human-like traits. 

### Key Features:
- A unique AI character with its own personality, daily routines, and preferences.
- Generation of diverse social media posts, including text, images, videos, and audio.
- Simulation of human-like behavior, such as daily activities, professional work, and hobbies.
- Utilizes AI APIs for creating content dynamically.

The project is designed to push the boundaries of simulating human behavior using AI, showcasing creativity and diversity in content generation.

---

## Getting Started
Follow the steps below to set up the project on your local machine and run the simulation.

### Prerequisites
Ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)
- Git (to clone the repository)

### Setup Instructions

#### 1. Clone the Repository
```bash
git clone https://github.com/Ankitsingh0805/PersonaVerse.git
```

#### 2. Create and Activate a Virtual Environment

**On Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the Simulation
```bash
python run_simulation.py
```

---

## How It Works
1. **Dynamic Personality**:
   - The AI character is designed with unique traits, routines, and preferences. These include its location, daily habits, food preferences, and more.

2. **Content Generation**:
   - The character generates social media posts daily, which may include text, images, videos, or audio.
   - Leverages AI APIs for diverse content creation, ensuring engaging and varied posts.

3. **Simulation File**:
   - `run_simulation.py` is the entry point of the project, which initializes the AI character and starts the simulation.

---

## File Structure
```plaintext
.
your_project_directory/
│
├── requirements.txt
├── run_simulation.py
├── main.py
│
├── config/
│   └── config.yaml
│
└── src/
    ├── __init__.py
    │
    ├── models/
    │   ├── __init__.py
    │   ├── character.py
    │   └── content.py
    │
    ├── generators/
    │   ├── __init__.py
    │   ├── character_generator.py
    │   └── content_generator.py
    │
    └── utils/
        ├── __init__.py
        ├── text_generation.py
        ├── image_generation.py
        ├── audio_generation.py
        └── video_generation.py
│
└── output/
    ├── indian/
    │   └── posts/
    └── korean/
        └── posts/         
```

---

## Future Improvements
- Add support for multi-character interaction.
- Enable real-time user input to influence the character's behavior.
- Expand the diversity of generated content, including live-stream simulations.

---

## Contributing
Feel free to contribute to this project! Open issues and pull requests are welcome. For major changes, please discuss them with the repository owners first.



---

## Contact
If you have any questions or suggestions, please reach out via ankitsingh21432143@gmail.com.
