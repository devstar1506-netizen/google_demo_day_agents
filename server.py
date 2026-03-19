import json
import sys
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
from agents import MainAgent

try:
    print("Loading agents...")
    main_agent = MainAgent()
    print("Agents ready.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

class AgentServer(SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[{self.path}]", format % args)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        if self.path == '/api/task':
            self._handle_task(post_data)
        elif self.path == '/api/review-pr':
            self._handle_review_pr(post_data)
        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, code, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(body)

    def _handle_task(self, post_data):
        try:
            req = json.loads(post_data.decode('utf-8'))
            task = req.get('task', '')
            t = task.lower()

            target = main_agent.python_coder
            agent_name = "coder"
            if 'security' in t or 'audit' in t or 'owasp' in t:
                target = main_agent.security_agent
                agent_name = "security"
            elif 'deploy' in t or 'build' in t or 'git' in t:
                target = main_agent.devops_agent
                agent_name = "devops"
            elif 'lint' in t or 'quality' in t or 'standard' in t:
                target = main_agent.python_standards
                agent_name = "standards"

            result = main_agent.delegate(task, target)
            self._send_json(200, {"status": "success", "agent": agent_name, "result": result})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _handle_review_pr(self, post_data):
        try:
            req = json.loads(post_data.decode('utf-8'))
            pr_number = req.get('pr_number', '')
            repo = req.get('repo', '')

            if not pr_number:
                self._send_json(400, {"error": "pr_number is required"})
                return

            # Build gh command
            cmd = f"gh pr diff {pr_number}"
            if repo:
                cmd += f" --repo {repo}"

            print(f"[*] Running: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/home/sandipdatta/Desktop/google_demo_day")

            if result.returncode != 0:
                self._send_json(500, {"error": result.stderr.strip() or "Could not fetch PR diff"})
                return

            diff = result.stdout.strip()
            if not diff:
                self._send_json(200, {"result": "The diff is empty — nothing to review."})
                return

            # Build the code review prompt
            task_prompt = (
                "Review the following git diff for a Pull Request. "
                "Provide a clear, concise, and actionable code review in markdown. "
                "Identify bugs, security vulnerabilities, and style issues.\n\n"
                f"```diff\n{diff[:6000]}\n```"
            )

            # Use Security + Standards agents for dual review
            sec_review = main_agent.security_agent.execute_task(task_prompt)
            std_review = main_agent.python_standards.execute_task(task_prompt)

            combined = (
                f"## 🔐 Security Agent Review\n\n{sec_review}\n\n"
                f"---\n\n"
                f"## 📐 Python Standards Review\n\n{std_review}"
            )

            self._send_json(200, {"status": "success", "result": combined, "pr_number": pr_number})

        except Exception as e:
            self._send_json(500, {"error": str(e)})


if __name__ == "__main__":
    PORT = 8000
    print(f"\n{'='*55}")
    print(f"🚀 Agent Server LIVE on http://localhost:{PORT}")
    print(f"{'='*55}")
    server = HTTPServer(('', PORT), AgentServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
