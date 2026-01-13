"""
Agent Runner 
This is used to run agents 
"""
class AgentRunner:
    def __init__(self, registry, memory, llm_client):
        self.registry = registry
        self.memory = memory
        self.llm = llm_client

    def run(self, agent_name, input, context):
        agent_cls = self.registry.get(agent_name)
        agent = agent_cls(context)

        # Inject memory
        context.memory = self.memory.load(context)

        try:
            output = agent.run(input)
            self.memory.save(context, output)
            return output
        except Exception as e:
            raise AgentExecutionError(agent_name, e)

