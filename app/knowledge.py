import re
import networkx as nx


class KnowledgeGraphBuilder:

    def __init__(self):
        # MultiDiGraph allows multiple relationships
        # between the same pair of concepts.
        self.graph = nx.MultiDiGraph()

    def clean_entity(self, text):

        text = text.strip()

        # Remove punctuation
        text = re.sub(
            r"^[^\w]+|[^\w]+$",
            "",
            text
        )

        # Remove articles
        text = re.sub(
            r"^(the|a|an)\s+",
            "",
            text,
            flags=re.IGNORECASE
        )

        # Normalize whitespace
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def add_relationship(self, source, relation, target):

        source = self.clean_entity(source)
        target = self.clean_entity(target)

        if not source or not target:
            return

        self.graph.add_node(source)
        self.graph.add_node(target)

        self.graph.add_edge(
            source,
            target,
            relation=relation
        )

    def extract_from_sentence(self, sentence):

        sentence = sentence.strip()

        # ------------------------------------------------
        # X is the [property] from Y
        # Example:
        # Earth is the third planet from the Sun.
        # ------------------------------------------------

        match = re.match(
            r"^(.*?)\s+is\s+the\s+(.*?)\s+from\s+(?:the\s+)?(.+?)\.?$",
            sentence,
            re.IGNORECASE
        )

        if match:

            subject = match.group(1)
            relation = match.group(2) + " from"
            object_ = match.group(3)

            self.add_relationship(
                subject,
                relation,
                object_
            )

            return True

        # ------------------------------------------------
        # X revolves around Y / X orbits Y
        # ------------------------------------------------

        match = re.match(
            r"^(.*?)\s+(revolves around|orbits)\s+(.+?)\.?$",
            sentence,
            re.IGNORECASE
        )

        if match:

            subject = match.group(1)
            relation = match.group(2)
            object_ = match.group(3)

            self.add_relationship(
                subject,
                relation,
                object_
            )

            return True

        # ------------------------------------------------
        # X has Y
        # ------------------------------------------------

        match = re.match(
            r"^(.*?)\s+has\s+(.+?)\.?$",
            sentence,
            re.IGNORECASE
        )

        if match:

            subject = match.group(1)
            object_ = match.group(2)

            self.add_relationship(
                subject,
                "has",
                object_
            )

            return True

        # ------------------------------------------------
        # X is Y
        # Generic rule — KEEP THIS LAST
        # ------------------------------------------------

        match = re.match(
            r"^(.*?)\s+is\s+(.+?)\.?$",
            sentence,
            re.IGNORECASE
        )

        if match:

            subject = match.group(1)
            object_ = match.group(2)

            self.add_relationship(
                subject,
                "is",
                object_
            )

            return True

        return False

    def build(self, text_lines):

        self.graph.clear()

        for line in text_lines:
            self.extract_from_sentence(line)

        return self.graph