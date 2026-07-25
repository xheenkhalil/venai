import os
import re

directory = r"c:\Users\USER\Desktop\venai\client\src\app"

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith(".tsx"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Replace basic string fetch
            new_content = re.sub(r'fetch\("http://localhost:8000/api/', r'fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/', content)
            
            # Replace template string fetch
            new_content = re.sub(r'fetch\(`http://localhost:8000/api/', r'fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/', new_content)
            
            # Replace ternaries
            new_content = re.sub(r'\? `http://localhost:8000/api/', r'? `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/', new_content)
            new_content = re.sub(r': `http://localhost:8000/api/', r': `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/', new_content)

            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated {path}")
