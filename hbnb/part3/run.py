import sys
import os
import webbrowser

# Chemin du projet
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("PYTHONPATH:", sys.path)  # Debug temporaire

from app import create_app
app = create_app()

# === Test endpoint pour debug POST ===
@app.route('/test_post', methods=['POST'])
def test_post():
    print("DEBUG: /test_post called")
    return {"ok": True}
# === Fin test endpoint ===

if __name__ == "__main__":
    # Ouvre Swagger UI automatiquement
    webbrowser.open("http://localhost:5001")
    
    print(app.url_map)
    # Lance le serveur sur le port 5001
    app.run(debug=True, host='0.0.0.0', port=5001)
