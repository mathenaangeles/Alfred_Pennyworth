# Alfred Pennyworth 

This is a multi-purpose Discord bot. It supports the following commands:

### Discord Utilities
- `create_channel` - Creates a new voice or text channel in a given category, if any
- `delete_channel` - Deletes an existing channel in a given category, if any
- `create_invite` - Creates an invite link to the server that is valid for 1 user
- `add_members` - Adds member/s to a specific channel
- `remove_members` - Removes members/s from a specific channel

### Others
- `roll` - Rolls a 6-sided dice
- `eight_ball` - Simulates a Magic 8 Ball
- `set_timer` - Sets a timer for the specified number of minutes

## Getting Started
1. Create a virtual environment and activate it.
2. Run `pip install requirements.txt` to install all dependencies.
3. Create a `.env` file with in the parent directory with the following contents:
```
TOKEN = <INSERT TOKEN HERE>
```
4. Run `python bot.py`.