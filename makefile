clean:
	rmdir /s /q __pycache__
	rmdir /s /q venv

run:
	venv\Scripts\activate && pip install -r requirements.txt && py main.py

freeze:
	venv\Scripts\activate && pip freeze > requirements.txt