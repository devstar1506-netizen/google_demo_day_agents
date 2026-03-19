import os

class Agent:
    def __init__(self, name: str, skill_file: str = None):
        self.name = name
        self.skills = []
        self.skill_instructions = ""
        
        # Load skills from the markdown file if provided
        if skill_file and os.path.exists(skill_file):
            with open(skill_file, 'r') as f:
                self.skill_instructions = f.read()
            
            # Extract bullet points as simple string skills for display/logging
            for line in self.skill_instructions.split('\n'):
                stripped = line.strip()
                if stripped.startswith('- '):
                    self.skills.append(stripped[2:])

    def add_skill(self, skill: str):
        if skill not in self.skills:
            self.skills.append(skill)
            self.skill_instructions += f"\n- {skill}"
            
    def execute_task(self, task: str) -> str:
        # Check if OpenAI is available and configured
        if os.getenv("OPENAI_API_KEY"):
            try:
                import openai
                client = openai.OpenAI()
                
                system_prompt = f"You are a highly experienced specialized agent named '{self.name}'.\n"
                if self.skill_instructions:
                    system_prompt += f"Here are your primary responsibilities and instructions:\n{self.skill_instructions}\n"
                system_prompt += "Review the task thoroughly and respond intelligently, clearly, and concisely. Use markdown."
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": task}
                    ],
                    max_tokens=600
                )
                
                return response.choices[0].message.content.strip()
            except ImportError:
                return f"[SIMULATED] (Please run 'pip install openai' to use the LLM backend.)\n {self.name} received task: '{task}'"
            except Exception as e:
                return f"[API ERROR: {e}]\n Fallback: {self.name} received task: '{task}'"
                
        # Default simulated fallback if no API KEY is found
        skills_str = ", ".join(self.skills) if self.skills else "no specific skills"
        return f"[MOCK] {self.name} (using skills: [{skills_str}]) completed task: '{task}'"

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
        
    def delegate(self, task: str, agent: Agent) -> str:
        result = agent.execute_task(task)
        return (f"{self.name} delegated task to {agent.name}...\n"
                f"--- {agent.name} Result ---\n"
                f"{result}\n"
                f"-------------------------------------\n")

if __name__ == "__main__":
    print("Welcome to the Agent Framework!")
    if not os.getenv("OPENAI_API_KEY"):
        print(">> No OPENAI_API_KEY detected. Running in MOCK mode.")
    main = MainAgent()
    print(main.delegate("Please audit the authentication pipeline.", main.security_agent))
