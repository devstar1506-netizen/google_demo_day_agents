import os
import urllib.request
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

class Agent:
    def __init__(self, name: str, skill_file: str = None):
        self.name = name
        self.skills = []
        self.skill_instructions = ""
        
        if skill_file and os.path.exists(skill_file):
            with open(skill_file, 'r') as f:
                self.skill_instructions = f.read()
            for line in self.skill_instructions.split('\n'):
                stripped = line.strip()
                if stripped.startswith('- '):
                    self.skills.append(stripped[2:])

    def add_skill(self, skill: str):
        if skill not in self.skills:
            self.skills.append(skill)
            self.skill_instructions += f"\n- {skill}"
            
    def _try_ollama(self, system_prompt: str, task: str) -> str | None:
        """Attempt to call local Ollama LLM. Returns None on failure."""
        try:
            full_prompt = f"### System\n{system_prompt}\n\n### User\n{task}\n\n### Response\n"
            payload = json.dumps({
                "model": "codellama:7b",
                "prompt": full_prompt,
                "stream": False
            }).encode('utf-8')
            
            req = urllib.request.Request(OLLAMA_URL, data=payload, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result.get('response', '').strip()
        except Exception:
            return None
    
    def _try_openai(self, system_prompt: str, task: str) -> str | None:
        """Attempt to call OpenAI API. Returns None on failure."""
        if not os.getenv("OPENAI_API_KEY"):
            return None
        try:
            import openai
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task}
                ],
                max_tokens=600
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return None

    def execute_task(self, task: str) -> str:
        system_prompt = f"You are a specialized agent named '{self.name}'.\n"
        if self.skill_instructions:
            system_prompt += f"Your capabilities:\n{self.skill_instructions}\n"
        system_prompt += "Respond clearly, intelligently, and concisely. Use markdown."
        
        # Priority: Ollama (local) → OpenAI → Mock
        result = self._try_ollama(system_prompt, task)
        if result:
            return f"[Ollama/codellama]\n{result}"
        
        result = self._try_openai(system_prompt, task)
        if result:
            return f"[OpenAI/gpt-4o-mini]\n{result}"
        
        skills_str = ", ".join(self.skills) if self.skills else "no specific skills"
        return f"[MOCK] {self.name} (skills: [{skills_str}]) completed: '{task}'"

class SecurityAgent(Agent):
    def __init__(self):
        super().__init__("Security Agent", "skills/security_agent.md")

class DevOpsDeploymentAgent(Agent):
    def __init__(self):
        super().__init__("DevOps Deployment Agent", "skills/devops_deployment_agent.md")

class PythonCoder(Agent):
    def __init__(self):
        super().__init__("Python Coder", "skills/python_coder.md")

class PythonCodingStandards(Agent):
    def __init__(self):
        super().__init__("Python Coding Standards", "skills/python_coding_standards.md")

class MainAgent(Agent):
    def __init__(self):
        super().__init__("Main Agent", "skills/main_agent.md")
        self.security_agent = SecurityAgent()
        self.devops_agent = DevOpsDeploymentAgent()
        self.python_coder = PythonCoder()
        self.python_standards = PythonCodingStandards()
        
    def delegate(self, task: str, agent: 'Agent') -> str:
        result = agent.execute_task(task)
        return (f"**{self.name}** delegated to **{agent.name}**\n\n"
                f"{result}\n")

if __name__ == "__main__":
    print("Welcome to the Agent Framework!")
    main = MainAgent()
    print(main.delegate("Audit the authentication pipeline for OWASP vulnerabilities.", main.security_agent))
