"""
Virtual agent team and task distribution.

After an email is classified, the task manager routes tasks to the
appropriate virtual agents:

- Reviewer     → reviews application quality (triggered for Zusagen)
- FeedbackWriter → drafts a polite reply (triggered for Absagen & Zusagen)
- Archiver     → archives the application with metadata (always)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agent.classifier import ClassificationResult
from agent.logger import get_logger

logger = get_logger("task_manager")


@dataclass
class Task:
    """Represents a unit of work assigned to a virtual agent."""

    agent_name: str
    role: str
    action: str
    message_id: str
    subject: str
    category: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed: bool = False
    result: Optional[str] = None


class VirtualAgent:
    """Base class for a virtual team member."""

    def __init__(self, name: str, role: str, description: str) -> None:
        self.name = name
        self.role = role
        self.description = description

    def execute(self, task: Task) -> str:
        """Execute a task and return a result description."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"VirtualAgent(name={self.name!r}, role={self.role!r})"


class ReviewerAgent(VirtualAgent):
    """Reviews an application for quality and completeness."""

    def execute(self, task: Task) -> str:
        logger.info(
            "[%s] Reviewing application for message %s ('%s').",
            self.name,
            task.message_id,
            task.subject,
        )
        # In a full implementation this could call OpenAI for deeper analysis.
        result = (
            f"Application '{task.subject}' reviewed by {self.name}. "
            f"Category: {task.category}. "
            "Flagged for human follow-up: no."
        )
        logger.info("[%s] Review complete: %s", self.name, result)
        return result


class FeedbackWriterAgent(VirtualAgent):
    """Drafts a polite reply email based on classification."""

    def execute(self, task: Task) -> str:
        category = task.category
        if category == "Absage":
            draft = (
                f"Sehr geehrte Damen und Herren,\n\n"
                f"vielen Dank für Ihre Bewerbung. Leider müssen wir Ihnen mitteilen, "
                f"dass wir Ihre Bewerbung nicht weiterverfolgen können.\n\n"
                f"Wir wünschen Ihnen für Ihre weitere Jobsuche viel Erfolg.\n\n"
                f"Mit freundlichen Grüßen,\nIhr Bewerbungs-Agent"
            )
        elif category == "Zusage":
            draft = (
                f"Sehr geehrte Damen und Herren,\n\n"
                f"vielen Dank für Ihre Einladung. Wir freuen uns sehr über die "
                f"positive Rückmeldung und werden uns zeitnah melden.\n\n"
                f"Mit freundlichen Grüßen,\nIhr Bewerbungs-Agent"
            )
        else:
            draft = (
                f"Sehr geehrte Damen und Herren,\n\n"
                f"vielen Dank für Ihre Nachricht. Wir werden uns um Ihr Anliegen kümmern.\n\n"
                f"Mit freundlichen Grüßen,\nIhr Bewerbungs-Agent"
            )

        logger.info(
            "[%s] Draft feedback prepared for message %s (category: %s).",
            self.name,
            task.message_id,
            category,
        )
        return draft


class ArchiverAgent(VirtualAgent):
    """Archives the application with metadata for traceability."""

    def execute(self, task: Task) -> str:
        import json
        from datetime import datetime, timezone

        record = {
            "message_id": task.message_id,
            "subject": task.subject,
            "category": task.category,
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "metadata": task.metadata,
        }
        logger.info(
            "[%s] Archived message %s: %s",
            self.name,
            task.message_id,
            json.dumps(record, ensure_ascii=False),
        )
        return f"Archived: {json.dumps(record, ensure_ascii=False)}"


_AGENT_REGISTRY: Dict[str, type] = {
    "review": ReviewerAgent,
    "feedback": FeedbackWriterAgent,
    "archive": ArchiverAgent,
}


class TaskManager:
    """Routes classification results to the appropriate virtual agents."""

    def __init__(self, team_config: List[Dict[str, str]]) -> None:
        self.agents: Dict[str, VirtualAgent] = {}
        for agent_cfg in team_config:
            role = agent_cfg["role"]
            agent_class = _AGENT_REGISTRY.get(role)
            if agent_class is None:
                logger.warning("Unknown agent role '%s' in config; skipping.", role)
                continue
            agent = agent_class(
                name=agent_cfg["name"],
                role=role,
                description=agent_cfg.get("description", ""),
            )
            self.agents[role] = agent
            logger.debug("Registered agent: %s", agent)

    def dispatch(self, result: ClassificationResult) -> List[Task]:
        """
        Create and execute tasks for a classification result.

        Returns the list of completed Task objects.
        """
        tasks = self._build_tasks(result)
        completed: List[Task] = []

        for task in tasks:
            agent = self.agents.get(task.role)
            if agent is None:
                logger.warning(
                    "No agent registered for role '%s'; skipping task '%s'.",
                    task.role,
                    task.action,
                )
                continue
            try:
                task.result = agent.execute(task)
                task.completed = True
                logger.info(
                    "Task '%s' completed by agent '%s' for message %s.",
                    task.action,
                    agent.name,
                    task.message_id,
                )
            except Exception as exc:
                logger.error(
                    "Task '%s' failed for agent '%s', message %s: %s",
                    task.action,
                    agent.name,
                    task.message_id,
                    exc,
                )
            completed.append(task)

        return completed

    # ------------------------------------------------------------------
    # Task construction
    # ------------------------------------------------------------------

    @staticmethod
    def _build_tasks(result: ClassificationResult) -> List[Task]:
        """Determine which tasks to create based on classification."""
        base = {
            "message_id": result.message_id,
            "subject": result.subject,
            "category": result.category,
            "metadata": {
                "summary": result.summary,
                "reasoning": result.reasoning,
            },
        }
        tasks: List[Task] = []

        # Always archive
        tasks.append(Task(agent_name="Archiver", role="archive", action="archive", **base))

        # Feedback for all classifications
        tasks.append(Task(agent_name="FeedbackWriter", role="feedback", action="draft_feedback", **base))

        # Additional review only for acceptances
        if result.is_acceptance:
            tasks.append(Task(agent_name="Reviewer", role="review", action="review_application", **base))

        return tasks
