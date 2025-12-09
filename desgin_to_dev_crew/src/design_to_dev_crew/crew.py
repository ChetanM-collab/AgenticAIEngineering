from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from design_to_dev_crew.tools.file_writer import WriteFileTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class DesignToDevCrew():
    """DesginToDevCrew crew"""

    # Optional: explicit config paths (these are also the defaults)
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # --- Agents -------------------------------------------------------------

    @agent
    def development_lead(self) -> Agent:
        return Agent(
            config=self.agents_config["development_lead"],
            tools=[WriteFileTool()],
            verbose=True,
        )

    @agent
    def backend_developer(self) -> Agent:
        return Agent(
            config=self.agents_config["backend_developer"],
            tools=[WriteFileTool()],
            verbose=True,
        )

    @agent
    def frontend_developer(self) -> Agent:
        return Agent(
            config=self.agents_config["frontend_developer"],
            tools=[WriteFileTool()],
            verbose=True,
        )

    @agent
    def tester(self) -> Agent:
        return Agent(
            config=self.agents_config["tester"],
            tools=[WriteFileTool()],
            verbose=True,
        )

    @agent
    def peer_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["peer_reviewer"],
            verbose=True,
        )

    # --- Tasks --------------------------------------------------------------

    @task
    def design_backend_frontend(self) -> Task:
        """Development lead produces the overall technical design."""
        return Task(
            config=self.tasks_config["design_backend_frontend"],
        )

    @task
    def implement_backend(self) -> Task:
        """Backend dev creates Spring Boot backend skeleton."""
        return Task(
            config=self.tasks_config["implement_backend"],
        )

    @task
    def implement_frontend(self) -> Task:
        """Frontend dev creates JS/React/Vue frontend skeleton."""
        return Task(
            config=self.tasks_config["implement_frontend"],
        )

    @task
    def create_test_plan(self) -> Task:
        """Tester creates test strategy + example tests."""
        return Task(
            config=self.tasks_config["create_test_plan"],
        )

    @task
    def peer_review_solution(self) -> Task:
        """Senior engineer reviews design, code, and tests."""
        return Task(
            config=self.tasks_config["peer_review_solution"],
        )

    # --- Crew ---------------------------------------------------------------

    @crew
    def crew(self) -> Crew:
        """
        Creates the design to dev crew.

        Task order is sequential:
        1) design_backend_frontend
        2) implement_backend
        3) implement_frontend
        4) create_test_plan
        5) peer_review_solution
        """
        return Crew(
            agents=self.agents,   # auto-collected from @agent methods
            tasks=self.tasks,     # auto-collected from @task methods
            process=Process.sequential,
            verbose=True,
        )