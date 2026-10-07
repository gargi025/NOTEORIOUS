from app.pipeline import HandwritingPipeline


IMAGE_PATH = "data/samples/current_upload.png"


pipeline = HandwritingPipeline()

output = pipeline.process(IMAGE_PATH)

results = output["lines"]
graph = output["graph"]


print("=" * 60)
print("NOTEORIOUS PROTOTYPE")
print("=" * 60)


for result in results:

    print(f"\nLine {result['line_number']}: {result['text']}")

    print(
        f"OCR confidence: "
        f"{result['confidence']:.4f}"
    )

    print(
        f"Semantic consistency: "
        f"{result['semantic_score']:.4f}"
    )

    print(
        f"KG consistent: "
        f"{result['kg_consistent']}"
    )

    print(
        f"Reliability: "
        f"{result['reliability_score']:.4f}"
    )

    print(
        f"Action: "
        f"{result['action']}"
    )

    print(
        f"Domain consistent: "
        f"{result['domain_consistent']}"
    )

    if result["kg_conflicts"]:

        print("KG conflicts:")

        for conflict in result["kg_conflicts"]:

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

    if result["domain_conflicts"]:
        print("Domain conflicts:")

        for conflict in result["domain_conflicts"]:
            print(
                f"  - {conflict['type']}: "
                f"{conflict.get('candidate_target', conflict.get('target'))}"
            )

print("\n" + "=" * 60)
print("KNOWLEDGE GRAPH")
print("=" * 60)

print("\nConcepts:")

for node in graph.nodes:

    print(f"  • {node}")


print("\nRelationships:")

for source, target, data in graph.edges(data=True):

    print(
        f"  {source} "
        f"--[{data['relation']}]--> "
        f"{target}"
    )


print("\n" + "=" * 60)