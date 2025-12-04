from anthropic import Anthropic
from dotenv import load_dotenv
import os
from pathlib import Path

env_test_path = Path(__file__).parent / ".env.test"
if env_test_path.exists():
    load_dotenv(env_test_path)

client = Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
)
page = client.models.list()
for model in page.data:
    print(model.id)