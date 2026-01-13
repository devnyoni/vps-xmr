import libvirt
import os
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# HTML DASHBOARD (HAPA NDIPO HTML YOTE IPO)
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>SMART VPS MANAGER</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body { background: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
        .card { background: #1e1e1e; border: 1px solid #333; color: white; border-radius: 12px; }
        .btn-primary { background: #007bff; border: none; }
        .status-on { color: #00ff88; font-weight: bold; }
        .status-off { color: #ff4444; font-weight: bold; }
    </style>
</head>
<body class="container py-5">
    <h1 class="mb-4">🚀 My VPS Engine</h1>
    
    <div class="card p-4 mb-4 shadow">
        <h3>Deploy New Instance</h3>
        <form action="/create" method="POST" class="row g-3">
            <div class="col-md-5">
                <input type="text" name="name" class="form-control" placeholder="Server Name (mf: vps-moja)" required>
            </div>
            <div class="col-md-3">
                <select name="ram" class="form-select">
                    <option value="1024">1GB RAM</option>
                    <option value="2048">2GB RAM</option>
                </select>
            </div>
            <div class="col-md-4">
                <button type="submit" class="btn btn-primary w-100">Washa Server Sasa</button>
            </div>
        </form>
    </div>

    <div class="card p-4 shadow">
        <h3>Live Servers</h3>
        <table class="table table-dark mt-3">
            <thead>
                <tr><th>Name</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
                {% for vps in vps_list %}
                <tr>
                    <td><strong>{{ vps.name }}</strong></td>
                    <td><span class="{{ 'status-on' if vps.active else 'status-off' }}">
                        {{ 'RUNNING' if vps.active else 'SHUTOFF' }}</span></td>
                    <td>
                        <a href="/action/start/{{ vps.name }}" class="btn btn-sm btn-success">Start</a>
                        <a href="/action/stop/{{ vps.name }}" class="btn btn-sm btn-warning">Stop</a>
                        <a href="/action/delete/{{ vps.name }}" class="btn btn-sm btn-danger">Delete</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

def get_conn():
    return libvirt.open('qemu:///system')

@app.route('/')
def home():
    conn = get_conn()
    domains = conn.listAllDomains()
    vps_list = [{"name": d.name(), "active": d.isActive()} for d in domains]
    conn.close()
    return render_template_string(HTML_LAYOUT, vps_list=vps_list)

@app.route('/create', methods=['POST'])
def create():
    name, ram = request.form['name'], request.form['ram']
    # 1. Tengeneza disk ya 10GB
    os.system(f"qemu-img create -f qcow2 /var/lib/libvirt/images/{name}.qcow2 10G")
    # 2. Soma XML
    with open('vps_template.xml', 'r') as f:
        xml = f.read().replace('{{ name }}', name).replace('{{ ram }}', ram)
    # 3. Washa VPS
    conn = get_conn()
    conn.defineXML(xml)
    dom = conn.lookupByName(name)
    dom.create()
    conn.close()
    return redirect('/')

@app.route('/action/<cmd>/<name>')
def action(cmd, name):
    conn = get_conn()
    dom = conn.lookupByName(name)
    if cmd == 'start': dom.create()
    elif cmd == 'stop': dom.destroy()
    elif cmd == 'delete':
        if dom.isActive(): dom.destroy()
        dom.undefine()
        os.system(f"rm /var/lib/libvirt/images/{name}.qcow2")
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
