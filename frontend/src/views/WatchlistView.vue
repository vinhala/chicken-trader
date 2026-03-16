<template>
  <section>
    <h2>Watchlist</h2>
    <div class="card">
      <label>Ticker<input v-model="ticker" /></label>
      <label>Name<input v-model="assetName" /></label>
      <button @click="add">Add</button>
      <p>{{ message }}</p>
    </div>
    <div v-for="w in items" :key="w.id" class="card">
      <strong>{{ w.ticker }}</strong> - {{ w.asset_name }}
      <button @click="remove(w.id)">Remove</button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../stores/api";

const items = ref<any[]>([]);
const ticker = ref("");
const assetName = ref("");
const message = ref("");

async function load() {
  try { items.value = await api("/watchlist"); }
  catch (e: any) { message.value = e.message; }
}
async function add() {
  try {
    await api("/watchlist", { method: "POST", body: JSON.stringify({ ticker: ticker.value, asset_name: assetName.value }) });
    ticker.value = "";
    assetName.value = "";
    await load();
  } catch (e: any) {
    message.value = e.message;
  }
}
async function remove(id: number) {
  await api(`/watchlist/${id}`, { method: "DELETE" });
  await load();
}
onMounted(load);
</script>
