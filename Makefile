run:
	poetry run python3 main.py

register $(scope):
	poetry run python3 scripts/register_commands.py scope

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete