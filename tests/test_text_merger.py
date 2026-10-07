from app.text_merger import merge_logical_lines


lines = [
    "The sun is a star .",
    "Earth is the third planet from the Sun .",
    "Earth revolves around the sun .",
    "Earth has a Moon .",
    "Mars is the fourth planet from the",
    "seen .",
]

merged = merge_logical_lines(lines)

print("=" * 60)
print("LOGICAL SENTENCES")
print("=" * 60)

for i, sentence in enumerate(merged, 1):
    print(f"{i}. {sentence}")