import libvirt
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# --- MUONEKANO (HTML/CSS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VPS Manager Pro</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body { background-color: #1a1a1a; color: white; font-family: sans-serif; }
        .card { background-color: #2d2d2d; border: none; color: white; margin-top: 20px; }
        .status-running { color: #00ff00; }
        .status-stopped { color: #ff4444; }
        .btn-primary { background-color: #007bff; border: none; }
    </style>
</head>
<body class="container py-5">
    <div class="d-flex justify-content-between align-items-center">
        <h1>🚀 VPS Control Panel</h1>
        <span class="badge bg-primary">KVM Engine v1.0</span>
    </div>

    <div class="card p-4 shadow">
        <h3>Create New Instance</h3>
        <form action="/create" method="POST" class="row g-3">
            <div class="col-md-4">
                <input type="text" name="name" class="form-control" placeholder="Jina la VPS (e.g. server-01)" required>
            </div>
            <div class="col-md-3">
                <select name="ram" class="form-select">
                    <option value="1024">1GB RAM</option>
                    <option value="2048">2GB RAM</option>
                    <option value="4096">4GB RAM</option>
                </select>
            </div>
            <div class="col-md-3">
                <button type="submit" class="btn btn-success w-100">Deploy Now</button>
            </div>
        </form>
    </div>

    <div class="card p-4 mt-4 shadow">
        <h3>Your Servers</h3>
        <table class="table table-dark table-hover mt-3">
            <thead>
                <tr>
                    <th>ID</th><th>Name</th><th>Status</th><th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for vps in vps_list %}
                <tr>
                    <td>{{ vps.id }}</td>
                    <td><strong>{{ vps.name }}</strong></td>
                    <td>
                        <span class="{{ 'status-running' if vps.active else 'status-stopped' }}">
                            ● {{ 'Running' if vps.active else 'Shut off' }}
                        </span>
                    </td>
                    <td>
                        <div class="btn-group">
                            <a href="/action/start/{{ vps.name }}" class="btn btn-sm btn-outline-success">Start</a>
                            <a href="/action/stop/{{ vps.name }}" class="btn btn-sm btn-outline-warning">Stop</a>
                            <a href="/action/delete/{{ vps.name }}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Una uhakika?')">Delete</a>
                        </div>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

# --- LOGIC (Back-end) ---

def get_connection():
    # Inaunganisha na KVM ya server yako
    return libvirt.open('qemu:///system')

@app.route('/')
def index():
    conn = get_connection()
    domains = conn.listAllDomains()
    vps_list = []
    for dom in domains:
        vps_list.append({
            "id": dom.ID() if dom.ID() != -1 else "-",
            "name": dom.name(),
            "active": dom.isActive()
        })
    conn.close()
    return render_template_string(HTML_TEMPLATE, vps_list=vps_list)

@app.route('/action/<cmd>/<name>')
def action(cmd, name):
    conn = get_connection()
    dom = conn.lookupByName(name)
    if cmd == 'start':
        dom.create()
    elif cmd == 'stop':
        dom.destroy()
    elif cmd == 'delete':
        if dom.isActive():
            dom.destroy()
        dom.undefine()
    conn.close()
    return redirect(url_for('index'))

@app.route('/create', methods=['POST'])
def create():
    name = request.form['name']
    ram = request.form['ram']
    # Hapa ndipo tutaunganisha na vps_template.xml baadae
    print(f"Tunatengeneza VPS: {name} yenye RAM: {ram}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
