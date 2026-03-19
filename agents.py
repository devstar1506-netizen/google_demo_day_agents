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
        skills_str = ", ".join(self.skills) if self.skills else "no specific skills"
        return f"{self.name} (using skills: [{skills_str}]) received task: '{task}'"

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
        return f"{self.name} is delegating to {agent.name}...\n  -> Result: {agent.execute_task(task)}"

if __name__ == "__main__":
    main = MainAgent()
    print("Agents successfully initialized with skills loaded from Markdown files.\n")
    print(main.delegate("Audit code repository for secrets", main.security_agent))
    print(main.delegate("Write tests for authentication", main.python_coder))
    
    # Example of adding a new skill dynamically
    print("\nAdding 'multi_cloud_architecture' skill to DevOps Deployment Agent...")
    main.devops_agent.add_skill("multi_cloud_architecture")
    print(main.delegate("Design scalable microservices", main.devops_agent))
