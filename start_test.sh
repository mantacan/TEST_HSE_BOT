#!/bin/bash

coverage erase

PYTHONPATH=$(pwd) coverage run --source=develop -m pytest tests/*.py

coverage report --include="develop/search.py,develop/location_manager.py,develop/database_manager.py"
coverage html --include="develop/search.py,develop/location_manager.py,develop/database_manager.py"

(cd htmlcov && python3 -m http.server 8000 &)
sleep 2
xdg-open http://localhost:8000/index.html 2>/dev/null || open http://localhost:8000/index.html 2>/dev/null
sleep 600
rm -rf htmlcov