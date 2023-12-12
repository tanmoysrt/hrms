/**
 * Will be moved to framework
 */

class FrappeNotification {
    static relayServerBaseURL = 'http://notification.relay:8000';

    // Constructor
    constructor(project_name, app_name) {
        this.project_name = project_name;
        this.app_name = app_name;
        this.token = null;
        this.messaging = null;
        this.initialized = false;
        this.onMessageHandler = null;
    }

    // Setup notification service
    async initialize() {
        if (this.initialized) {
            return;
        }
        // fetch web config
        let url = `${FrappeNotification.relayServerBaseURL}/api/method/notification_relay.api.get_config?project_name=${this.project_name}&app_name=${this.app_name}`
        let response = await fetch(url);
        let config = await response.json();
        // encode config to pass to service worker
        const encodeConfig = encodeURIComponent(JSON.stringify(config));
        const serviceWorkerURL = `/assets/hrms/frontend/frappe-notification-sw.js?config=${encodeConfig}`;
        // register service worker
        if ("serviceWorker" in navigator) {
            const registration = await navigator.serviceWorker.register(serviceWorkerURL);
            console.log("SW registered:", registration);
            // initialize firebase
            firebase.initializeApp(config);
            // // initialize messaging
            this.messaging = firebase.messaging();
            this.messaging.useServiceWorker(registration);
            if(this.onMessageHandler) {
                this.onMessage(this.onMessageHandler);
            }
        }
        this.initialized = true;
    }

    // Enable notification
    async enableNotification() {
        // Return if token already presence in the instance
        if (this.token != null) {
            return {
                permission_granted: true,
                token: this.token,
            };
        }
        if (this.messaging == null) {
            throw new Error("Notification service not initialized");
        }
        // check in local storage for old token
        let old_token = localStorage.getItem('firebase_token');
        // new token
        let new_token = "";
        try {
            // request permission and get token
            new_token = await this.messaging.getToken();
        } catch {
            // permission denied
            return {
                permission_granted: false,
                token: ""
            };
        }
        // check if token is changed
        let token_changed = old_token !== new_token;
        // send token to server
        if (token_changed) {
            // unsubscribe old token
            // TODO: url will be same when it will merge in framework
            if (old_token) {
                await fetch("/api/method/hrms.api.unsubscribe_push_notification?fcm_token=" + new_token, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
            }
            // subscribe push notification and register token
            // TODO: url will be same when it will merge in framework
            let response = await fetch("/api/method/hrms.api.subscribe_push_notification?fcm_token=" + new_token, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            if (response.status !== 200) {
                throw new Error("Failed to subscribe to push notification");
            }
            // save token to local storage
            localStorage.setItem('firebase_token', new_token);
        }

        return {
            permission_granted: true,
            token: new_token
        };
    }

    // Add Listener
    onMessage(callback) {
        this.onMessageHandler = callback;
        if (this.messaging == null) {
            return;
        }
        this.messaging.onMessage(callback);
    }
}