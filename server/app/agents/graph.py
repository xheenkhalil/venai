from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.supervisor import supervisor_node
from app.agents.research import research_node
from app.agents.calling import calling_node
from app.agents.analysis import analysis_node
from app.agents.report import report_node

def route_from_supervisor(state: AgentState):
    route = state.get("next_agent", "FINISH")
    if route == "FINISH":
        return END
    return route

workflow = StateGraph(AgentState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("research", research_node)
workflow.add_node("calling", calling_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("report", report_node)

workflow.set_entry_point("supervisor")

workflow.add_edge("research", "supervisor")
workflow.add_edge("calling", "supervisor")
workflow.add_edge("analysis", "supervisor")
workflow.add_edge("report", "supervisor")

workflow.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "research": "research",
        "calling": "calling",
        "analysis": "analysis",
        "report": "report",
        END: END
    }
)

app_graph = workflow.compile()
