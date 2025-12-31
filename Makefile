clean:
	rmdir /s /q __pycache__
	rmdir /s /q venv

run:
	source venv\bin\activate & pip install -r requirements.txt & python main.py

freeze:
	source venv\bin\activate & pip freeze > requirements.txt