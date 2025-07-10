# CLI Tool Tests

This directory contains tests for the Insurance Letter CLI tool.

## Test Files

- `test_conversation.py` - Tests the CLI conversation display feature
- `demo_conversation.py` - Demo script showing agent conversation functionality

## Running Tests

### Run Conversation Tests

```bash
cd cli-tool/tests
python test_conversation.py
```

This will test:
- Direct mode with conversation display
- Direct mode without conversation display
- Interactive mode behavior
- JSON output format

### Run Demo Script

```bash
cd cli-tool/tests
python demo_conversation.py
```

This demonstrates:
- Full agent conversation with approval workflow
- How conversation data is structured
- Different approval scenarios

## Prerequisites

- Python 3.8+
- CLI dependencies installed
- API services available (for demo script)

## Writing New Tests

When adding new CLI tests:

1. Create test files in this directory
2. Import the CLI using: `Path(__file__).parent.parent / "insurance_cli.py"`
3. Use subprocess to run CLI commands and capture output
4. Assert on expected output patterns

Example test structure:

```python
def test_cli_feature():
    args = ["--option", "value"]
    returncode, stdout, stderr = run_cli_command(args)
    
    assert returncode == 0
    assert "expected output" in stdout
```