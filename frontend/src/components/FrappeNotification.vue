<template>
  <Dialog v-model="dialog">
    <template #body-title>
      <h3>{{ notificationTitle }}</h3>
    </template>
    <template #body-content>
      <p v-html="notificationBody"></p>
    </template>
  </Dialog>
</template>
<script setup>
import { ref, onMounted } from "vue";
import { Dialog } from "frappe-ui";

const dialog = ref(false);
const notificationTitle = ref("");
const notificationBody = ref("");

onMounted(() => {
		window.frappeNotification.onMessage((payload) => {
			notificationTitle.value = payload.data.title;
			notificationBody.value = payload.data.body;
			dialog.value = true;
		});
});
</script>