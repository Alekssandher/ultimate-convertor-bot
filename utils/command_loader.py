import asyncio
import importlib.util
from pathlib import Path
import logging
from discord import app_commands


async def load_command_module(command_name: str, commands_dir: Path):
    """Load a command module from the commands folder if not already loaded."""
    file_path = commands_dir / f"{command_name}.py"
    if not file_path.exists():
        logging.error(f"Command file {file_path} not found")
        return None

    try:
        spec = importlib.util.spec_from_file_location(command_name, file_path)
        if spec is None or spec.loader is None:
            logging.error(f"Could not load spec or loader for {file_path}")
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, 'execute'):
            logging.error(f"Module {command_name} missing execute function")
            return None

        logging.info(f"Loaded command module: {command_name}")
        return module
    except Exception as e:
        logging.error(f"Failed to load command {command_name}: {e}")
        return None

async def register_commands(bot, commands_dir: Path):
    """Register all commands from the commands directory."""
    for file in commands_dir.glob("*.py"):
        command_name = file.stem
        module = await load_command_module(command_name, commands_dir)
        if not module:
            continue

        if not hasattr(module, "name") or not hasattr(module, "description"):
            logging.warning(f"Skipping {command_name}: missing name or description")
            continue
        if not hasattr(module, "execute") or not asyncio.iscoroutinefunction(module.execute):
            logging.warning(f"Skipping {command_name}: execute must be async")
            continue

        try:
            cmd = app_commands.Command(
                name=module.name.lower(),
                description=module.description,
                callback=module.execute
            )
            bot.tree.add_command(cmd)
            logging.info(f"Registered command: {module.name}")
        except Exception as e:
            logging.error(f"Failed to register {module.name}: {e}")