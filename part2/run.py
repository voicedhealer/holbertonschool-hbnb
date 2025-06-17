import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# ou, pour être sûr :
# sys.path.insert(0, '/home/choisy/holbertonschool-hbnb/part2/')

print("PYTHONPATH:", sys.path)  # Debug temporairefrom app import create_app

from app import create_app


app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
