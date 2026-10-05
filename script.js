const chatToggleBtn = document.getElementById('chat-toggle-btn');
const chatBox = document.getElementById('chat-box');
const closeChat = document.getElementById('close-chat');
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

let step = 0; // لتتبع الخطوات
let userData = { name: '', phone: '' };

// فتح وغلق الشات
chatToggleBtn.addEventListener('click', () => {
    chatBox.classList.toggle('hidden');
    if (step === 0) {
        startChat();
    }
});

closeChat.addEventListener('click', () => {
    chatBox.classList.add('hidden');
});

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.textContent = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function startChat() {
    step = 1;
    appendMessage("أهلاً بك! ما هو اسمك؟", "bot");
}

function handleUserResponse() {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage(text, "user");
    userInput.value = "";

    if (step === 1) {
        userData.name = text;
        step = 2;
        setTimeout(() => {
            appendMessage(`أهلاً بك يا ${userData.name}. من فضلك اكتب رقم التليفون؟`, "bot");
        }, 600);
    } 
    else if (step === 2) {
        userData.phone = text;
        step = 3; // الخطوة الأخيرة (يسكت بعدها)
        setTimeout(() => {
            appendMessage("هيتم التواصل معاك عن طريق الواتساب.", "bot");
            // قفل خانة الكتابة والإرسال عشان يسكت تماماً
            userInput.disabled = true;
            sendBtn.disabled = true;
            userInput.placeholder = "تم إرسال بياناتك بنجاح";
        }, 600);
    }
}

sendBtn.addEventListener('click', handleUserResponse);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleUserResponse();
    }
});
