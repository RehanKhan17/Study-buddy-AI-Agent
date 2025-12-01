// ====== CONFIG ======
const BACKEND_URL = "http://127.0.0.1:8000/chat"; // change if needed

// ====== DOM ======
const chatWindow = document.getElementById('chatWindow');
const sendBtn = document.getElementById('sendBtn');
const userInput = document.getElementById('userInput');
const msgTpl = document.getElementById('msgTpl');
const breathBtn = document.getElementById('breathBtn');
const breathHelper = document.getElementById('breathHelper');
const breathCount = document.getElementById('breathCount');
const stopBreath = document.getElementById('stopBreath');
const voiceBtn = document.getElementById('voiceBtn');
const ttsBtn = document.getElementById('ttsBtn');
const themeToggle = document.getElementById('themeToggle');
const actionPanel = document.getElementById('actionPanel');
const tools = document.querySelectorAll('.tool');
const exportBtn = document.getElementById('exportBtn');
const clearBtn = document.getElementById('clearBtn');
const pageTitle = document.getElementById('pageTitle');

let breathInterval = null;
let history = JSON.parse(localStorage.getItem('chat_history_v1') || '[]');
let ttsEnabled = false;
let recognition = null;
let listening = false;

// restore history UI
history.forEach(h => appendMessage(h.text, h.who, false));

// mode switching
tools.forEach(t => t.addEventListener('click', () => {
  tools.forEach(x=>x.classList.remove('active')); t.classList.add('active');
  const m = t.dataset.mode;
  pageTitle.innerText = {
    chat:'Student Support Agent',
    study:'Study Helper',
    coping:'Coping Exercises — Grounding',
    safety:'Safety & Escalation'
  }[m] || 'Student Support Agent';
  if(m === 'coping') appendMessage('Try a short grounding exercise: name 5 things you can see.','bot');
}));

// append message
function appendMessage(text, who='bot', save=true){
  const node = msgTpl.content.cloneNode(true);
  const row = node.querySelector('.msg-row');
  const bubble = row.querySelector('.bubble');
  if(who === 'user'){ row.classList.add('right'); row.querySelector('.avatar').style.background = 'linear-gradient(90deg,#7c3aed,#06b6d4)'; }
  bubble.innerText = text;
  chatWindow.appendChild(node);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  if(save) {
    history.push({who,text,ts:Date.now()});
    localStorage.setItem('chat_history_v1', JSON.stringify(history));
  }
  return row;
}

// typing indicator
function showTyping(){
  const t = appendMessage('Typing...','bot', false);
  t.querySelector('.bubble').style.opacity = 0.7;
  return t;
}

// send message
async function sendMessage(){
  const text = userInput.value.trim();
  if(!text) return;
  appendMessage(text,'user');
  userInput.value = '';
  const typingRow = showTyping();
  try {
    const res = await fetch(BACKEND_URL, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    typingRow.remove();
    const reply = data?.reply || data?.response || 'No reply from server.';
    appendMessage(reply,'bot');
    if(ttsEnabled) speakText(reply);
  } catch(err){
    typingRow.remove();
    appendMessage('⚠️ Error contacting server.','bot');
    console.error(err);
  }
}

// keyboard + button
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', e => { if(e.key === 'Enter') sendMessage(); });

// BREATH HELPER
function startBreathing(){
  if(breathInterval) return;
  breathHelper.classList.remove('hidden');
  let s = 0; breathCount.innerText = '0';
  breathInterval = setInterval(()=> { s++; breathCount.innerText = s; }, 1000);
}
function stopBreathingFunc(){
  if(!breathInterval) return;
  clearInterval(breathInterval); breathInterval=null; breathHelper.classList.add('hidden'); breathCount.innerText='0';
}
breathBtn.addEventListener('click', startBreathing);
stopBreath.addEventListener('click', stopBreathingFunc);

// VOICE INPUT (Web Speech API)
if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.onresult = (evt) => {
    const t = evt.results[0][0].transcript;
    userInput.value = t;
    sendMessage();
  };
  recognition.onend = ()=> { listening=false; voiceBtn.classList.remove('listening'); }
  recognition.onerror = (e)=> { console.error(e); listening=false; voiceBtn.classList.remove('listening'); }
  voiceBtn.addEventListener('click', ()=>{
    if(listening){ recognition.stop(); listening=false; voiceBtn.classList.remove('listening'); }
    else { recognition.start(); listening=true; voiceBtn.classList.add('listening'); }
  });
} else {
  voiceBtn.style.opacity = 0.5;
  voiceBtn.title = 'Voice input not supported in this browser';
}

// TTS
function speakText(txt){
  if(!('speechSynthesis' in window)) return;
  const ut = new SpeechSynthesisUtterance(txt);
  ut.lang = 'en-US';
  window.speechSynthesis.speak(ut);
}
ttsBtn.addEventListener('click', ()=>{ ttsEnabled = !ttsEnabled; ttsBtn.classList.toggle('active'); });

// THEME TOGGLE
themeToggle.addEventListener('change', ()=>{
  if(themeToggle.checked){ document.body.classList.remove('dark'); document.body.classList.add('light'); }
  else { document.body.classList.remove('light'); document.body.classList.add('dark'); }
});

// EXPORT & CLEAR
exportBtn.addEventListener('click', ()=>{
  const csv = history.map(h=>`"${new Date(h.ts).toISOString()}","${h.who}","${h.text.replace(/"/g,'""')}"`).join('\n');
  const blob = new Blob([csv], {type:'text/csv'}); const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = 'chat_history.csv'; a.click(); URL.revokeObjectURL(url);
});
clearBtn.addEventListener('click', ()=>{ chatWindow.innerHTML=''; history=[]; localStorage.removeItem('chat_history_v1'); });

// initial welcome
if(history.length === 0){
  setTimeout(()=>appendMessage('Hi — I am Study buddy. How can I help you today?','bot'), 700);
}
