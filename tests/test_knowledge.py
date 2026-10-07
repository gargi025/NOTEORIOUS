from app.knowledge import KnowledgeGraphBuilder


lines = [
    "The Sun is a star.",
    "Earth is the third planet from the Sun.",
    "Earth revolves around the Sun.",
    "Earth has the Moon.",
    "Mars is the fourth planet from the Sun."
]


builder = KnowledgeGraphBuilder()
graph = builder.build(lines)


print("=" * 60)
print("NOTEORIOUS KNOWLEDGE GRAPH")
print("=" * 60)

print("\nConcepts:")

for node in graph.nodes:
    print(f"  • {node}")


print("\nRelationships:")

for source, target, data in graph.edges(data=True):
    print(
        f"  {source} --[{data['relation']}]--> {target}"
    )

print("\n" + "=" * 60)