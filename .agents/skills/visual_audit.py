# Instructions for QAGuardian
# 1. Open browser in iPhone 15 Pro viewport (393x852).
# 2. Run JS snippet to check for element overlaps:
#    "const all = document.querySelectorAll('*'); 
#     checkIfElementsOverlap(all);"
# 3. If any element has a width greater than the viewport (393px), trigger a "Horizontal Overflow" failure.
# 4. Check 'Green Velvet' modals for centering; if top/left offset is not proportional, fail[cite: 26].