from app.knowledge import KnowledgeGraphBuilder
from app.kg_consistency import check_kg_consistency


builder = KnowledgeGraphBuilder()

existing_lines = [
    "The Sun is a star.",
    "Earth is the third planet from the Sun.",
    "Earth revolves around the Sun.",
    "Earth has the Moon.",
    "Mars is the fourth planet from the Sun."
]

graph = builder.build(existing_lines)


tests = [
    "Earth revolves around the Sun.",
    "Earth revolves around the Moon.",
]


for candidate in tests:

    result = check_kg_consistency(
        graph,
        candidate,
        builder
    )

    print("=" * 60)
    print("Candidate:")
    print(candidate)

    print("\nConsistent:", result["consistent"])

    if result["conflicts"]:
        print("\nConflicts:")

        for conflict in result["conflicts"]:
            print(
                f"  Existing: "
                f"{conflict['source']} "
                f"--[{conflict['relation']}]--> "
                f"{conflict['existing_target']}"
            )

            print(
                f"  Candidate: "
                f"{conflict['source']} "
                f"--[{conflict['relation']}]--> "
                f"{conflict['candidate_target']}"
            )         
            

    print()
