<template>
	<ion-page>
		<ion-header class="ion-no-border">
			<div class="w-full sm:w-96">
				<div class="flex flex-col bg-white shadow-sm p-4">
					<div class="flex flex-row justify-between items-center">
						<div class="flex flex-row items-center gap-2">
							<h2 class="text-xl font-bold text-gray-900">
								{{ props.pageTitle }}
							</h2>
						</div>
						<div class="flex flex-row items-center gap-3 ml-auto">
							<Button :variant="'solid'"
							        theme="gray"
							        size="sm"
							        label="Button"
							        :loading="pushNotificationState.value === 2"
							        :loadingText="Activating"
							        :disabled="pushNotificationState.value === 2"
							        :link="null"
							        @click="subscribeToNotifications"
							>
								{{ pushNotificationState.value === 1 ? "Push Activated" : "Push Enable" }}
							</Button>
							<router-link
									:to="{ name: 'Notifications' }"
									v-slot="{ navigate }"
									class="flex flex-col items-center"
							>
								<span class="relative inline-block" @click="navigate">
									<FeatherIcon name="bell" class="h-6 w-6"/>
									<span
											v-if="unreadNotificationsCount.data"
											class="absolute top-0 right-0.5 inline-block w-2 h-2 bg-red-600 rounded-full border border-white"
									>
									</span>
								</span>
							</router-link>
							<router-link
									:to="{ name: 'Profile' }"
									class="flex flex-col items-center"
							>
								<Avatar
										:image="user.data.user_image"
										:label="user.data.first_name"
										size="xl"
								/>
							</router-link>
						</div>
					</div>
				</div>
			</div>
		</ion-header>

		<ion-content class="ion-no-padding">
			<FrappeNotification />
			<div class="flex flex-col h-screen w-screen sm:w-96">
				<slot name="body"></slot>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonHeader, IonContent, IonPage } from "@ionic/vue"
import { onMounted, ref, inject } from "vue"
import { FeatherIcon, Avatar, Button } from "frappe-ui"

import { unreadNotificationsCount } from "@/data/notifications"
import FrappeNotification from "@/components/FrappeNotification.vue";

const user = inject("$user")
const socket = inject("$socket")

const props = defineProps({
	pageTitle: {
		type: String,
		required: false,
		default: "Frappe HR",
	},
})

onMounted(() => {
	socket.on("hrms:update_notifications", () => {
		unreadNotificationsCount.reload()
	})
})

// Notification Enabling State
const pushNotificationState = ref(0)

// 0 - not enabled, 1- enabled, 2- loading
function subscribeToNotifications() {
	pushNotificationState.value = 2;
	window.frappeNotification.enableNotification()
			.then((data) => {
				console.log(data);
				let permission_granted = data.permission_granted;
				let token = data.token;
				if (permission_granted) {
					alert("Permission Granted");
					alert("Token: " + token);
					pushNotificationState.value = 1;
				} else {
					alert("Permission Denied ! Retry again later");
					pushNotificationState.value = 0;
				}
			})
			.catch((err) => {
				console.log(err);
				pushNotificationState.value = 0;
			})
}
</script>
