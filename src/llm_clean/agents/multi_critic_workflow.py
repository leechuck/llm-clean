from langchain_core.messages import SystemMessage, HumanMessage
from llm_clean.utils.llm import get_chat_model
from llm_clean.agents.workflow import OntoCleanWorkflow
from llm_clean.agents.critic_prompts import (
    RIGIDITY_CRITIC_PROMPT,
    IDENTITY_CRITIC_PROMPT,
    UNITY_CRITIC_PROMPT,
    DEPENDENCE_CRITIC_PROMPT,
)


class MultiCriticWorkflow(OntoCleanWorkflow):
    """
    Extends OntoCleanWorkflow with 4 specialized critic agents — one per
    OntoClean meta-property (Rigidity, Identity, Unity, Dependence).

    The taxonomist proposal loop and retry logic are inherited unchanged.
    Only _critique_link is overridden to fan out to the individual critics.

    The rejection_threshold controls how many critics must reject before a
    link is rejected:
      - threshold=1 (default, strict): any single property violation rejects
        the link, which is the theoretically correct OntoClean behaviour
      - threshold=2 (majority): at least 2 critics must reject, which is
        more tolerant of false positives from small models
    """

    def __init__(self, model_id: str, rejection_threshold: int = 1):
        super().__init__(model_id)
        self.rejection_threshold = rejection_threshold
        self.critics = {
            "rigidity": {
                "model": get_chat_model(model_id),
                "prompt": RIGIDITY_CRITIC_PROMPT,
            },
            "identity": {
                "model": get_chat_model(model_id),
                "prompt": IDENTITY_CRITIC_PROMPT,
            },
            "unity": {
                "model": get_chat_model(model_id),
                "prompt": UNITY_CRITIC_PROMPT,
            },
            "dependence": {
                "model": get_chat_model(model_id),
                "prompt": DEPENDENCE_CRITIC_PROMPT,
            },
        }

    def _critique_link(self, term: str, parent: str, domain: str) -> str:
        """Run all 4 property critics and aggregate their verdicts.

        A link is rejected when the number of rejecting critics meets or
        exceeds self.rejection_threshold.  All rejecting critics' feedback
        is aggregated and passed back to the taxonomist for retry.
        """
        user_msg = f'Taxonomist proposes: "{term}" IS-A "{parent}". Domain: {domain}'

        rejections = []
        for name, critic in self.critics.items():
            messages = [
                SystemMessage(content=critic["prompt"]),
                HumanMessage(content=user_msg),
            ]
            response = critic["model"].invoke(messages)
            content = response.content
            if "REJECT" in content.upper():
                rejections.append(f"[{name}] {content}")

        if len(rejections) >= self.rejection_threshold:
            return "REJECT: " + " | ".join(rejections)

        return "APPROVE"
