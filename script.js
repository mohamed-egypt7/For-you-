// كود الجافاسكريبت اللي هيكون في صفحة الـ Vercel ليرسل إشعار لتليجرام مباشرة
const BOT_TOKEN = "8989450747:AAFQ56vM9mniwelDaqf5zqc76J2f3zorpE0";
const CHAT_ID = "8718173410";

function sendToTelegram(messageText) {
    const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            chat_id: CHAT_ID,
            text: messageText
        })
    });
}
