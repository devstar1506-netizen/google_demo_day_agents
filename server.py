import json
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from agents import MainAgent

# Initialize the globally shared Python agents
try:
    print("Loading LLM Agents into memory...")
    main_agent = MainAgent()
except Exception as e:
    print(f"Error initializing agents: {e}")
    sys.exit(1)

class AgentServer(SimpleHTTPRequestHandler):
    
    def end_headers(self):
        # Insert CORS headers seamlessly
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
        
    def do_POST(self):
        if self.path == '/api/task':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                request_json = json.loads(post_data.decode('utf-8'))
                task = request_json.get('task', '')
                
                # Execute simple Python-level routing (acts as a middleware orchestrator)
                target_agent = main_agent.python_coder
                agent_name = "coder"
                
                t = task.lower()
                if 'security' in t or 'audit' in t or 'penetration' in t or 'owasp' in t:
                    target_agent = main_agent.security_agent
                    agent_name = "security"
                elif 'deploy' in t or 'build' in t or 'git' in t:
                    target_agent = main_agent.devops_agent
                    agent_name = "devops"
                elif 'lint' in t or 'quality' in t or 'standard' in t:
                    target_agent = main_agent.python_standards
                    agent_name = "standards"

                print(f"[*] Received /api/task payload -> Routing to {target_agent.name}")
                
                # Actually route the task through the Python LLM Pipeline!
                raw_result = main_agent.delegate(task, target_agent)
                
                # Build the dynamic UI payload
                response_data = {
                    "status": "success",
                    "agent": agent_name,
                    "result": raw_result
                }
                
                # Stream the response flawlessly to the browser
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    PORT = 8000
    server = HTTPServer(('', PORT), AgentServer)
    print(f"\n=======================================================")
    print(f"🚀 Python Full-Stack Agent Server is LIVE on Port {PORT}")
    print(f"=======================================================")
    print("Serving HTML/JS frontend files and intercepting /api/task POST requests...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully.")
        server.server_close()
