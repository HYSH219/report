# AI Tool Call Client

This is a Python client that allows AI assistants to call various tools, including a skill loading functionality.

## Features

- File operations: list, rename, delete, create, read files
- Web content fetching
- Chat history searching
- AnythingLLM API integration
- Skill loading functionality

## Skill System

### load_skill_content Function

The `load_skill_content` function is used to load the content of a skill's SKILL.md file. It:

1. Takes a skill name as parameter
2. Loads the corresponding SKILL.md file from the skills directory
3. Parses and removes YAML front matter
4. Returns the content after the front matter

### Creating a Skill

To create a new skill:

1. Create a directory under the `skills` folder with the skill name
2. Create a `SKILL.md` file in that directory
3. Include YAML front matter (optional) with skill metadata
4. Add the skill content after the front matter

### Example: Notice Skill

The `notice` skill is included as an example. It is used for writing, modifying, and polishing notices. The skill requires:

- Notices should not start with "通知" (Notice)
- Notices must have a prefix like "XX部" (Department)
- If no department is provided, use "XX部" as placeholder

## Usage

1. Create a `.env` file based on `.env.example` and configure your API keys
2. Run the client: `python tool_call_client.py`
3. When the AI assistant needs to use a skill, it will call `load_skill_content` to load the skill's instructions

## Testing

To test the skill loading functionality:

1. Run the test script: `python tool_call_client.py`
2. The test will load the `notice` skill and display its content
3. It will also show example outputs for notice writing scenarios

## Directory Structure

```
.
├── skills/
│   └── notice/
│       └── SKILL.md
├── .env
├── .env.example
├── tool_call_client.py
└── README.md
```