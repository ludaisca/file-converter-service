
import re

content_default = '<policy domain="coder" rights="none" pattern="PDF" />'
content_variation_1 = '<policy domain="coder" rights="none" pattern="PDF"/>'
content_variation_2 = '<policy domain="coder" rights="none" pattern="PDF"  />'

# Current sed pattern in Dockerfile (translated to python regex)
# s/<policy domain="coder" rights="none" pattern="PDF" \/>/<policy domain="coder" rights="read|write" pattern="PDF" \/>/g
# Regex: <policy domain="coder" rights="none" pattern="PDF" />
regex_current = r'<policy domain="coder" rights="none" pattern="PDF" />'

replacement = '<policy domain="coder" rights="read|write" pattern="PDF" />'

print("Testing Current Regex:")
print(f"Match Default: {bool(re.search(regex_current, content_default))}")
print(f"Match Variation 1: {bool(re.search(regex_current, content_variation_1))}")
print(f"Match Variation 2: {bool(re.search(regex_current, content_variation_2))}")

# Proposed better regex
# s/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/g
regex_improved = r'rights="none" pattern="PDF"'

print("\nTesting Improved Regex:")
print(f"Match Default: {bool(re.search(regex_improved, content_default))}")
print(f"Match Variation 1: {bool(re.search(regex_improved, content_variation_1))}")
print(f"Match Variation 2: {bool(re.search(regex_improved, content_variation_2))}")
