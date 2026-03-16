<template>
  <section>
    <h2>Opportunity Detail</h2>
    <div v-if="store.selected" class="card">
      <h3>{{ store.selected.headline }}</h3>
      <p><strong>Event summary:</strong> {{ store.selected.event_summary }}</p>
      <p><strong>Market interpretation:</strong> {{ store.selected.market_impact }}</p>
      <p><strong>Context:</strong> {{ store.selected.context }}</p>
      <p><strong>Risks:</strong> {{ store.selected.risk_factors }}</p>
      <p><strong>Conditions:</strong> {{ store.selected.thesis_conditions }}</p>
      <h4>Suggested Securities</h4>
      <p v-if="store.selected.assets_warning">{{ store.selected.assets_warning }}</p>
      <ul v-if="store.selected.assets.length">
        <li v-for="asset in store.selected.assets" :key="asset.ticker">
          <strong>{{ asset.ticker }}</strong> - {{ asset.asset_name }} ({{ asset.asset_type }}) / {{ asset.direction }}
        </li>
      </ul>
      <button @click="follow">Follow investment idea</button>
      <p>{{ message }}</p>
    </div>
    <p v-else-if="store.error">{{ store.error }}</p>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useOpportunitiesStore } from "../stores/opportunities";

const route = useRoute();
const store = useOpportunitiesStore();
const message = ref("");

onMounted(() => store.loadDetail(String(route.params.id)));

async function follow() {
  try {
    await store.follow(String(route.params.id));
    message.value = "Thesis followed successfully.";
  } catch (e: any) {
    message.value = e.message;
  }
}
</script>
