const input = document.getElementById('taskInput');
const btn = document.getElementById('dispatchBtn');
const terminal = document.getElementById('terminalOutput');

// Reference DOM nodes for the agents
const agents = {
    main: document.getElementById('agent-main'),
    security: document.getElementById('agent-security'),
    devops: document.getElementById('agent-devops'),
    coder: document.getElementById('agent-coder'),
    standards: document.getElementById('agent-standards')
};

// Helper: Convert newlines to breaks and simple markdown bold to HTML
// Since the real LLM output might return beautiful markdown syntax!
function parseMarkdownToHTML(text) {
    return text.replace(/\n/g, '<br>')
               .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
               .replace(/```([\s\S]*?)```/g, '<pre style="background: rgba(0,0,0,0.4); padding: 10px; border-radius: 5px;">$1</pre>');
}

function logToTerminal(message, type = 'sys') {
    const el = document.createElement('div');
    el.className = `log-entry ${type}`;
    el.innerHTML = parseMarkdownToHTML(message);
    terminal.appendChild(el);
    terminal.scrollTop = terminal.scrollHeight;
}

function setAgentStatus(agentId, isActive) {
    const card = agents[agentId];
    if (!card) return;
    const statusEl = card.querySelector('.status');
    
    if (isActive) {
        card.classList.add('active');
        statusEl.textContent = 'Working...';
        statusEl.className = 'status indicator-active';
    } else {
        card.classList.remove('active');
        statusEl.textContent = 'Idle';
        statusEl.className = 'status indicator-idle';
    }
}

// Handle Dispatch logic using Real REST API connections to Python!
btn.addEventListener('click', async () => {
    const task = input.value.trim();
    if (!task) return;
    
    input.value = '';
    logToTerminal(`${task}`, 'user');
    
    // Step 1: Main agent picks it up visually
    setAgentStatus('main', true);
    logToTerminal('<strong>Main Agent</strong>: "Transmitting payload to the Python `/api/task` backend via HTTP POST..."', 'agent');
    
    try {
        // Ping our new live python backend!
        const response = await fetch('/api/task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: task })
        });
        
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.error || 'Server error');
        
        // Turn off main agent focus, light up the sub-agent dynamically based on python routing
        const targetAgent = data.agent;
        setAgentStatus('main', false);
        if (agents[targetAgent]) setAgentStatus(targetAgent, true);
        
        // Print the real intelligent python execution output received via the network!
        logToTerminal(`[SYSTEM: API RESPONSE HTTP 200 RECEIVED FROM PYTHON SERVER]`, 'sys');
        logToTerminal(data.result, 'agent');
        
        // Return to idle gracefully
        if (agents[targetAgent]) setAgentStatus(targetAgent, false);
        logToTerminal(`Execution pipeline terminated. System awaiting next query.`, 'sys');
        
    } catch (err) {
        setAgentStatus('main', false);
        logToTerminal(`Error communicating with Python backend: ${err.message}`, 'sys');
    }
});

// Allow hitting Enter to submit input
input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') btn.click();
});
