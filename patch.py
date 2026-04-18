import sys

with open('c:/things/makeathon/req_gatherer.py', 'r', encoding='utf8') as f:
    text = f.read()

text = text.replace(
    "  async def stream_query(self, query: str, user_id: str = 'test') -> Any:",
    "  def query(self, query: str, user_id: str = 'test') -> Any:\n    return self.app.query(message=query, user_id=user_id)\n\n  async def stream_query(self, query: str, user_id: str = 'test') -> Any:"
)

with open('c:/things/makeathon/req_gatherer.py', 'w', encoding='utf8') as f:
    f.write(text)
