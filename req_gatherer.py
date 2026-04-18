from typing import Any

from google.adk.agents import llm_agent
from google.adk.sessions import vertex_ai_session_service
from google.adk.sessions import in_memory_session_service
from vertexai.preview.reasoning_engines import AdkApp
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context


VertexAiSessionService = vertex_ai_session_service.VertexAiSessionService
InMemorySessionService = in_memory_session_service.InMemorySessionService

class ProducerAgent:

  def __init__(self):
    self.app = None

  def session_service_builder(self):
    return InMemorySessionService()

  def set_up(self):
    """Sets up the ADK application."""
    compliance_requirements__fg__google_search_agent = llm_agent.LlmAgent(
      name='Compliance_Requirements__FG__google_search_agent',
      model='gemini-2.5-flash',
      description=(
          'Agent specialized in performing Google searches.'
      ),
      sub_agents=[],
      instruction='Use the GoogleSearchTool to find information on the web.',
      tools=[
        GoogleSearchTool()
      ],
    )
    compliance_requirements__fg__url_context_agent = llm_agent.LlmAgent(
      name='Compliance_Requirements__FG__url_context_agent',
      model='gemini-2.5-flash',
      description=(
          'Agent specialized in fetching content from URLs.'
      ),
      sub_agents=[],
      instruction='Use the UrlContextTool to retrieve content from provided URLs.',
      tools=[
        url_context
      ],
    )
    root_agent = llm_agent.LlmAgent(
      name='producer_agent',
      model='gemini-2.5-flash',
      description=(
          ''
      ),
      sub_agents=[],
      instruction='''Find EU/US compliance requirements for a product's raw materials. 
EU: pre-market, authorized substances only, food-grade, traceability, EFSA safety. 
US: post-market, cGMP (21 CFR 111), ID/purity testing, supplier qualification. Be very concise.''',
      tools=[
        agent_tool.AgentTool(agent=compliance_requirements__fg__google_search_agent),
        agent_tool.AgentTool(agent=compliance_requirements__fg__url_context_agent)
      ],
    )

    self.app = AdkApp(
        agent=root_agent,
        session_service_builder=self.session_service_builder
    )

  def query(self, query: str, user_id: str = 'test') -> Any:
    return self.app.query(message=query, user_id=user_id)

  async def stream_query(self, query: str, user_id: str = 'test') -> Any:
    """Streaming query."""
    async for chunk in self.app.async_stream_query(
        message=query,
        user_id=user_id,
    ):
      yield chunk


producer_app = ProducerAgent()


class SupplierAgent:

  def __init__(self):
    self.app = None

  def session_service_builder(self):
    return InMemorySessionService()

  def set_up(self):
    """Sets up the ADK application."""
    requirements_satisfier_google_search_agent = llm_agent.LlmAgent(
      name='Requirements_Satisfier_google_search_agent',
      model='gemini-2.5-flash',
      description=(
          'Agent specialized in performing Google searches.'
      ),
      sub_agents=[],
      instruction='Use the GoogleSearchTool to find information on the web.',
      tools=[
        GoogleSearchTool()
      ],
    )
    requirements_satisfier_url_context_agent = llm_agent.LlmAgent(
      name='Requirements_Satisfier_url_context_agent',
      model='gemini-2.5-flash',
      description=(
          'Agent specialized in fetching content from URLs.'
      ),
      sub_agents=[],
      instruction='Use the UrlContextTool to retrieve content from provided URLs.',
      tools=[
        url_context
      ],
    )
    root_agent = llm_agent.LlmAgent(
      name='supplier_agent',
      model='gemini-2.5-flash',
      description=(
          ''
      ),
      sub_agents=[],
      instruction='''Search web to infer EU/US compliance levels a raw material satisfies.
EU: pre-market, authorized, food-grade, traceable, EFSA.
US: cGMP (21 CFR 111), ID/purity tests, qualified supplier. 
Evaluate raw material against these and be highly concise.''',
      tools=[
        agent_tool.AgentTool(agent=requirements_satisfier_google_search_agent),
        agent_tool.AgentTool(agent=requirements_satisfier_url_context_agent)
      ],
    )

    self.app = AdkApp(
        agent=root_agent,
        session_service_builder=self.session_service_builder
    )

  def query(self, query: str, user_id: str = 'test') -> Any:
    return self.app.query(message=query, user_id=user_id)

  async def stream_query(self, query: str, user_id: str = 'test') -> Any:
    """Streaming query."""
    async for chunk in self.app.async_stream_query(
        message=query,
        user_id=user_id,
    ):
      yield chunk

supplier_app = SupplierAgent()
