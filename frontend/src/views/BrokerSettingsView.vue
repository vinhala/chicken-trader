<template>
  <section>
    <h2>Broker Settings</h2>
    <div class="card">
      <label>Preferred Broker<input v-model="brokerName" /></label>
      <label>Preferred Exchanges<input v-model="exchanges" placeholder="NYSE,NASDAQ" /></label>
      <button @click="save">Save</button>
      <p>{{ message }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../stores/api";

const brokerName = ref("Default");
const exchanges = ref("");
const message = ref("");

onMounted(async () => {
  try {
    const data = await api("/broker/settings");
    brokerName.value = data.broker_name;
    exchanges.value = data.preferred_exchanges;
  } catch (e: any) {
    message.value = e.message;
  }
});

async function save() {
  try {
    await api("/broker/settings", {
      method: "PUT",
      body: JSON.stringify({ broker_name: brokerName.value, preferred_exchanges: exchanges.value }),
    });
    message.value = "Saved.";
  } catch (e: any) {
    message.value = e.message;
  }
}
</script>
