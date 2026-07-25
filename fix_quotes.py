import os
import re

directory = r"c:\Users\USER\Desktop\venai\client\src\app"

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith(".tsx"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # The previous script replaced fetch("http... with fetch(`${...
            # but left the closing quote " instead of backtick `
            # This regex finds those broken strings and fixes the closing quote.
            new_content = re.sub(r'(\$\{process\.env\.NEXT_PUBLIC_API_URL[^}]*\}/api/[^"]*)"', r'\1`', content)

            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Fixed {path}")
