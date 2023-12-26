import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getMessaging, onBackgroundMessage } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-sw.js";

const jsonConfig = new URL(location).searchParams.get('config');
const firebaseApp = initializeApp(JSON.parse(jsonConfig));
const messaging = getMessaging(firebaseApp);

onBackgroundMessage(messaging, (payload) => {
    console.log('[firebase-messaging-sw.js] Received background message ', payload);
    const notificationTitle = payload.data.title;
    const notificationOptions = {
        body: payload.data.body || '',
        data: { url:payload.data.click_action }
    };
    self.registration.showNotification(notificationTitle, notificationOptions);
});

self.addEventListener('notificationclick', (event)=>{
  event.notification.close();
  if(!event.notification.data.url){
        clients.openWindow(event.notification.data.url)
  };
})