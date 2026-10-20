import os
import re
from abc import ABC, abstractmethod

from .schemas import StructuredProposal


class LLMClient(ABC):
    @abstractmethod
    def parse_order_request(self, text, contacts, products) -> StructuredProposal:
        """Return data only; providers have no database or execution tools."""


class FakeLLMClient(LLMClient):
    def parse_order_request(self, text, contacts, products) -> StructuredProposal:
        match = re.fullmatch(r"\s*(\d+)\s+(.+?)\s+pour\s+(.+?)\s*", text, re.IGNORECASE)
        if not match:
            raise ValueError("Use '<quantity> <exact product name> pour <exact client name>'")
        quantity, product_name, contact_name = match.groups()
        clients = [
            c
            for c in contacts
            if c["nom"].casefold() == contact_name.casefold() and c["type"] == "client"
        ]
        matches = [p for p in products if p["nom"].casefold() == product_name.casefold()]
        if len(clients) != 1 or len(matches) != 1:
            raise ValueError("Product and client names must each identify exactly one record")
        return StructuredProposal(
            contact_id=clients[0]["id"],
            lines=[{"product_id": matches[0]["id"], "quantite": int(quantity)}],
            reasoning="Fake parser matched the quantity, exact product name and exact client name.",
        )


class RealLLMClient(LLMClient):
    def parse_order_request(self, text, contacts, products) -> StructuredProposal:
        # TODO: implement a provider call and validate its result as StructuredProposal.
        # Never give a provider database access or order-creation tools.
        raise NotImplementedError("Real LLM provider is a TODO; set LLM_PROVIDER=fake")


def get_llm_client() -> LLMClient:
    return FakeLLMClient() if os.getenv("LLM_PROVIDER", "fake") == "fake" else RealLLMClient()
