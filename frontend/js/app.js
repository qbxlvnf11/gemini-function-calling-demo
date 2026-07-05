document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chatMessages');
    const logsContainer = document.getElementById('logsContainer');
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const toolStatus = document.getElementById('toolStatus');
    const toolStatusText = document.getElementById('toolStatusText');
    const sendBtn = document.getElementById('sendBtn');
    
    // Modal Elements
    const navMain = document.getElementById('navMain');
    const navLogs = document.getElementById('navLogs');
    const navSettings = document.getElementById('navSettings');
    const settingsModal = document.getElementById('settingsModal');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    
    // Tab Switching Logic
    navMain.addEventListener('click', () => {
        navMain.classList.add('active');
        navLogs.classList.remove('active');
        chatMessages.classList.remove('hidden');
        logsContainer.classList.add('hidden');
        document.querySelector('.chat-input-area').style.display = 'block';
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });

    navLogs.addEventListener('click', () => {
        navLogs.classList.add('active');
        navMain.classList.remove('active');
        logsContainer.classList.remove('hidden');
        chatMessages.classList.add('hidden');
        document.querySelector('.chat-input-area').style.display = 'none';
        logsContainer.scrollTop = logsContainer.scrollHeight;
    });

    // Settings Modal Logic
    navSettings.addEventListener('click', () => {
        settingsModal.classList.remove('hidden');
    });

    closeSettingsBtn.addEventListener('click', () => {
        settingsModal.classList.add('hidden');
    });

    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) {
            settingsModal.classList.add('hidden');
        }
    });

    // Connect WebSocket
    const wsUrl = `ws://${window.location.host}/ws/chat`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('Connected to WebSocket server');
        document.querySelector('.status-indicator').style.backgroundColor = '#10b981';
        document.querySelector('.status-indicator').style.boxShadow = '0 0 8px #10b981';
    };

    ws.onclose = () => {
        console.log('Disconnected from WebSocket server');
        document.querySelector('.status-indicator').style.backgroundColor = '#ef4444';
        document.querySelector('.status-indicator').style.boxShadow = '0 0 8px #ef4444';
        document.querySelector('.status-panel span').textContent = 'System Offline';
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'message') {
            appendMessage(data.role, data.text);
            hideStatus();
        } else if (data.type === 'status') {
            if (data.text) {
                showStatus(data.text);
            } else {
                hideStatus();
            }
        } else if (data.type === 'tool_call') {
            appendToolCall(data.name, data.args);
        } else if (data.type === 'tool_result') {
            appendToolResult(data.name, data.result);
        } else if (data.type === 'ticket_update') {
            updateTicketUI(data.data);
        } else if (data.type === 'message_stream') {
            appendStreamChunk('model', data.text);
            hideStatus();
        } else if (data.type === 'message_stream_end') {
            finalizeStreamMessage();
        } else if (data.type === 'error') {
            appendMessage('model', `❌ ${data.text}`);
            hideStatus();
        }
    };

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = messageInput.value.trim();
        if (!text) return;

        // Display user message
        appendMessage('user', text);
        
        const payload = {
            text: text,
            model: document.getElementById('modelSelect').value,
            routing_mode: document.getElementById('routingModeSelect').value,
            router_model: document.getElementById('routerModelSelect') ? document.getElementById('routerModelSelect').value : 'gemini-2.5-flash'
        };
        
        // Send to server
        ws.send(JSON.stringify(payload));
        
        // Clear input
        messageInput.value = '';
        messageInput.focus();
    });

    function appendMessage(role, text) {
        // 1. Add to Main Chat
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.innerHTML = formatText(text);
        msgDiv.appendChild(bubble);
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // 2. Add to Logs
        const logDiv = document.createElement('div');
        logDiv.className = `message ${role}`;
        const logBubble = document.createElement('div');
        logBubble.className = 'message-bubble';
        logBubble.innerHTML = `<strong>${role.toUpperCase()}</strong>: <br>` + formatText(text);
        logDiv.appendChild(logBubble);
        logsContainer.appendChild(logDiv);
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    function appendToolCall(name, args) {
        const traceDiv = document.createElement('div');
        traceDiv.className = 'tool-trace-call';
        
        let argsStr = typeof args === 'object' ? JSON.stringify(args) : args;
        traceDiv.innerHTML = `<div class="tool-trace-title">⚙️ 도구 실행: ${name}</div><div>Parameters: ${argsStr}</div>`;
        
        // Tool traces ONLY go to logsContainer
        logsContainer.appendChild(traceDiv);
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    function appendToolResult(name, result) {
        const traceDiv = document.createElement('div');
        traceDiv.className = 'tool-trace-result';
        
        let resultStr = typeof result === 'object' ? JSON.stringify(result, null, 2) : result;
        traceDiv.innerHTML = `<div class="tool-trace-title">✅ 실행 결과: ${name}</div><div>${resultStr}</div>`;
        
        // Tool traces ONLY go to logsContainer
        logsContainer.appendChild(traceDiv);
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    let activeStreamBubbleMain = null;
    let activeStreamBubbleLog = null;
    let streamTextBuffer = "";

    function appendStreamChunk(role, text) {
        if (!activeStreamBubbleMain) {
            // 1. Create Main Chat Bubble
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${role}`;
            activeStreamBubbleMain = document.createElement('div');
            activeStreamBubbleMain.className = 'message-bubble stream-typing';
            msgDiv.appendChild(activeStreamBubbleMain);
            chatMessages.appendChild(msgDiv);

            // 2. Create Log Bubble
            const logDiv = document.createElement('div');
            logDiv.className = `message ${role}`;
            activeStreamBubbleLog = document.createElement('div');
            activeStreamBubbleLog.className = 'message-bubble stream-typing';
            logDiv.appendChild(activeStreamBubbleLog);
            logsContainer.appendChild(logDiv);
            
            streamTextBuffer = "";
        }

        streamTextBuffer += text;
        const formatted = formatText(streamTextBuffer);
        
        activeStreamBubbleMain.innerHTML = formatted;
        activeStreamBubbleLog.innerHTML = `<strong>${role.toUpperCase()}</strong>: <br>` + formatted;

        chatMessages.scrollTop = chatMessages.scrollHeight;
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    function finalizeStreamMessage() {
        if (activeStreamBubbleMain) {
            activeStreamBubbleMain.classList.remove('stream-typing');
            activeStreamBubbleLog.classList.remove('stream-typing');
            activeStreamBubbleMain = null;
            activeStreamBubbleLog = null;
            streamTextBuffer = "";
        }
    }

    function showStatus(text) {
        toolStatusText.textContent = text;
        toolStatus.classList.add('active');
    }

    function hideStatus() {
        toolStatus.classList.remove('active');
    }

    function formatText(text) {
        // Simple formatting to handle basic markdown/newlines
        return text.replace(/\n/g, '<br>')
                   .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    // Ticket UI Updater
    window.updateTicketUI = function(state) {
        if (!state) return;

        const ticketIntent = document.getElementById('ticketIntent');
        const ticketOrder = document.getElementById('ticketOrder');
        const ticketUrgency = document.getElementById('ticketUrgency');
        const ticketSummary = document.getElementById('ticketSummary');

        function updateField(element, value) {
            if (value && element.innerText !== value) {
                element.innerText = value;
                const parent = element.closest('.ticket-item');
                parent.classList.add('updated');
                setTimeout(() => parent.classList.remove('updated'), 1000);
            }
        }

        if (state.intent) updateField(ticketIntent, state.intent);
        if (state.order_number) updateField(ticketOrder, state.order_number);
        if (state.urgency) {
            updateField(ticketUrgency, state.urgency);
            if (state.urgency.toLowerCase() === 'high') {
                ticketUrgency.style.color = '#ef4444';
            } else {
                ticketUrgency.style.color = '#f8fafc';
            }
        }
        if (state.summary) updateField(ticketSummary, state.summary);
    };
});
