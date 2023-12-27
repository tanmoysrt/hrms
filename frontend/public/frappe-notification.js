/**
 * Will be moved to framework
 */
import {initializeApp} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import {
	getMessaging,
	getToken,
	onMessage,
	isSupported,
	deleteToken
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging.js";

class FrappeNotification {
	static relayServerBaseURL = 'https://push-notification-relay.frappe.cloud';

	// Constructor
	constructor(project_name, app_name) {
		this.project_name = project_name;
		this.app_name = app_name;
		this.app = null;
		this.token = null;
		this.messaging = null;
		this.serviceWorkerRegistration = null;
		this.initialized = false;
		this.vapid_public_key = "";
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
		let response_json = await response.json();
		let config = response_json.config;
		// set vapid public key
		this.vapid_public_key = response_json.vapid_public_key;
		// encode config to pass to service worker
		const encode_config = encodeURIComponent(JSON.stringify(config));
		const service_worker_URL = `/assets/hrms/frontend/frappe-notification-sw.js?config=${encode_config}`;
		// register service worker
		if ("serviceWorker" in navigator) {
			// check if service worker is already registered
			const registrations = await navigator.serviceWorker.getRegistrations();
			for (let i = 0; i < registrations.length; i++) {
				let registration = registrations[i];
				if (registration.active.scriptURL && registration.active.scriptURL.includes(service_worker_URL)) {
					console.log("SW already registered:", registration);
					this.serviceWorkerRegistration = registration;
					// activate service worker
					await registration.update();
					break;
				}
			}
			if (this.serviceWorkerRegistration == null) {
				const registration = await navigator.serviceWorker.register(service_worker_URL, {
					type: "module",
				});
				console.log("SW registered:", registration);
				this.serviceWorkerRegistration = registration;
			} else {
				console.log("SW already registered:", this.serviceWorkerRegistration);
			}

			// initialize firebase
			const firebaseApp = initializeApp(config);
			this.app = firebaseApp;
			// // initialize messaging
			this.messaging = getMessaging(firebaseApp);
			if (this.onMessageHandler) {
				this.onMessage(this.onMessageHandler);
			}
		}
		this.initialized = true;
	}

	// Enable notification
	async enableNotification() {
		if (!await isSupported()) {
			alert("Your browser does not support push notification");
			return;
		}
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
		// ask for permission
		const permission = await Notification.requestPermission();
		if (permission !== "granted") {
			return {
				permission_granted: false,
				token: "",
			};
		}

		// check in local storage for old token
		let old_token = localStorage.getItem('firebase_token');
		// new token
		let new_token = "";
		try {
			// request permission and get token
			new_token = await getToken(this.messaging, {
				vapidKey: this.vapid_public_key,
				serviceWorkerRegistration: this.serviceWorkerRegistration,
			})
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
			if (old_token) {
				await fetch("/api/method/hrms.api.unsubscribe_push_notification?fcm_token=" + old_token, {
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

		this.token = new_token;

		return {
			permission_granted: true,
			token: new_token
		};
	}

	async disableNotification() {
		if (this.token == null) {
			// try to fetch token from local storage
			this.token = localStorage.getItem('firebase_token');
			if (this.token == null || this.token === "") {
				return;
			}
		}
		// delete old token
		try {
			await deleteToken(this.messaging)
		} catch (e) {
			console.log("Failed to delete token from firebase");
		}
		// unsubscribe old token
		// TODO: url will be same when it will merge in framework
		try {
			await fetch("/api/method/hrms.api.unsubscribe_push_notification?fcm_token=" + this.token, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json',
				}
			});
		} catch {
			console.log("Failed to unsubscribe from push notification");
		}
		// remove token from local storage
		localStorage.removeItem('firebase_token');
		// reset state
		this.token = null;
	}

	// Add Listener
	onMessage(callback) {
		this.onMessageHandler = callback;
		if (this.messaging == null) {
			return;
		}
		onMessage(this.messaging, this.onMessageHandler)
	}
}

export default FrappeNotification