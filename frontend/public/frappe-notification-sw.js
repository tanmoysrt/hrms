// It's required to keep the file in the root directory of your web app.
if ('function' === typeof importScripts) {
    importScripts("https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js");
    importScripts("https://www.gstatic.com/firebasejs/8.10.1/firebase-messaging.js");

    const jsonConfig = new URL(location).searchParams.get('config');
    setup(JSON.parse(jsonConfig));

    // Setup firebase messaging
    function setup(config) {
        const firebaseConfig = config;

        firebase.initializeApp(firebaseConfig);
        const messaging = firebase.messaging();

        messaging.onBackgroundMessage(function(payload) {
            console.log('[firebase-messaging-sw.js] Received background message ', payload);
            const notificationTitle = payload.data.title;
            const notificationOptions = {
                body: payload.data.body || ''
            };
            self.registration.showNotification(notificationTitle, notificationOptions);
        });
    }
}