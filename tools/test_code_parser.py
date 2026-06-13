"""Quick smoke test for services.code_parser."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.code_parser import build_zip, download_label_for_file, parse_code_output

SAMPLE = """Hier ist dein Login-System:

```html
<!-- file: login.html -->
<!DOCTYPE html>
<html><body>Login</body></html>
```

```css
/* file: styles.css */
body { margin: 0; }
```

```javascript
// file: app.js
document.querySelector('form');
```
"""


def main() -> None:
    files = parse_code_output(SAMPLE)
    assert len(files) == 3, files
    assert files[0].filename == "login.html"
    assert files[0].extension == "html"
    assert files[1].filename == "styles.css"
    assert files[2].filename == "app.js"
    assert download_label_for_file(files[0]) == "Herunterladen als HTML"
    assert build_zip(files)[:2] == b"PK"

    single = parse_code_output("```html\n<!DOCTYPE html><html></html>\n```")
    assert len(single) == 1
    assert single[0].filename == "index.html"
    assert single[0].extension == "html"

    print("OK - code parser tests passed")


if __name__ == "__main__":
    main()
