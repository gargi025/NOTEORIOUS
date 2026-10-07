from app.semantic_consistency import calculate_semantic_consistency


candidate = "Earth revolves around the Sun."

context = """
Earth is the third planet from the Sun.
The Sun is a star.
Mars is the fourth planet from the Sun.
"""


score = calculate_semantic_consistency(
    candidate,
    context
)


print("=" * 60)
print("SEMANTIC CONSISTENCY TEST")
print("=" * 60)

print("\nCandidate:")
print(candidate)

print("\nContext:")
print(context)

print(f"\nSemantic score: {score:.4f}")

print("=" * 60)
