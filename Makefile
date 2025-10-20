run:
	poetry run python3 main.py

register $(scope):
	poetry run python3 scripts/register_commands.py scope