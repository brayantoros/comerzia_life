cd C:\Users\SENA\Desktop\comerzia

# Crea test_imports.py (si ya existe, sobrescribe)
@"
try:
    import sys, os
    import flask
    import mysql.connector
    from werkzeug.security import generate_password_hash, check_password_hash
    from werkzeug.utils import secure_filename
    print('Imports OK')
    print('Python:', sys.version.split()[0])
    print('Executable:', sys.executable)
    print('Flask:', flask.__version__)
    import werkzeug
    print('Werkzeug:', werkzeug.__version__)
except Exception as e:
    import traceback
    traceback.print_exc()
"@ > test_imports.py

# Ejecuta el test
python test_imports.py
