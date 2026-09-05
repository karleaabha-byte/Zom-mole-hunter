# ZOM-MOLE HUNTER — Python + HTML/CSS

No Streamlit. Python owns the game state and Zephyr's utility-based agent; the browser provides the dossier-style frontend.

## Run locally

```bash
cd zom_mole_python_web
python app.py
```

Open `http://127.0.0.1:8000`.

## Game logic
- Storage is the only 50/50 random event, rolled once per new case.
- After Storage is known, Zephyr's utility agent decides whether to deploy the secondary Wordle security lock.
- During interrogation, Zephyr evaluates truth vs. lie using the current evidence/security state and selects the action with higher utility.
- Raw utility scores are not shown to the player.
- There is no suspicion meter.
- Open a New Case creates a fresh Python `GameState` and returns to the opening page.

## Deploy on PythonAnywhere

1. Push this folder to GitHub. Do not commit `__pycache__` or secrets.
2. In PythonAnywhere, open a Bash console and clone the repository:

	```bash
	git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
	cd YOUR_REPOSITORY
	python3.11 -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt
	```

3. Open the **Web** tab, choose **Add a new web app**, select **Manual configuration**, and choose the same Python version.
4. Set the source directory to the cloned folder and the virtualenv to its `.venv` path.
5. Open the WSGI configuration file and replace its contents with:

   ```python
   import sys

   project = "/home/YOUR_USERNAME/YOUR_REPOSITORY"
   if project not in sys.path:
	   sys.path.insert(0, project)

   from app import app as application
   ```

6. Reload the web app. The public URL will be `https://YOUR_USERNAME.pythonanywhere.com`.

The Flask app in `app.py` is used for both local development and PythonAnywhere deployment.

## Publish through itch.io

The game needs Python to keep each player's game state, so do not upload only `index.html` as a standalone itch.io HTML5 game. First deploy it on PythonAnywhere, then create an itch.io project page and add the PythonAnywhere URL as the game's external play link. Players can launch it in their browser from itch.io.

For a native itch.io embed, the backend must also be hosted somewhere that allows cross-origin requests and credentials; the PythonAnywhere URL is the simplest reliable option for this project.
