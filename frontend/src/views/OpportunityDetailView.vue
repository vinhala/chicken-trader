<template>
  <section>
    <div class="section-heading">
      <span style="font-size: 1.5rem;">📊</span>
      <h2>OPPORTUNITY REPORT</h2>
    </div>

    <div v-if="store.error && !store.selected" class="mario-error">{{ store.error }}</div>

    <div v-if="store.loading" class="mario-empty">
      <ChickenLoader label="FETCHING REPORT..." />
    </div>

    <AppCard v-if="store.selected">
      <h3>{{ store.selected.headline }}</h3>
      <p style="font-size: 0.7rem; opacity: 0.6; margin-bottom: 1rem;">Generated: {{ new Date(store.selected.created_at).toLocaleString() }}</p>

      <div class="detail-section">
        <span class="mario-badge mario-badge--sector detail-section-label">Event</span>
        <p>{{ store.selected.event_summary }}</p>
      </div>

      <div class="detail-section">
        <span class="mario-badge mario-badge--sector detail-section-label">Market Impact</span>
        <p>{{ store.selected.market_impact }}</p>
      </div>

      <div class="detail-section">
        <span class="mario-badge mario-badge--sector detail-section-label">Context</span>
        <p>{{ store.selected.context }}</p>
      </div>

      <div class="detail-section">
        <span class="mario-badge mario-badge--warning detail-section-label">Risks</span>
        <p>{{ store.selected.risk_factors }}</p>
      </div>

      <div class="detail-section">
        <span class="mario-badge mario-badge--active detail-section-label">Thesis Conditions</span>
        <p>{{ store.selected.thesis_conditions }}</p>
      </div>

      <div v-if="store.selected.assets && store.selected.assets.length" class="detail-section">
        <h4>SUGGESTED SECURITIES</h4>
        <div v-if="store.selected.assets_warning" class="mario-card mario-card--yellow" style="margin-bottom: 0.75rem;">
          <p style="margin: 0; color: #000; font-size: 0.8rem;">⚠️ {{ store.selected.assets_warning }}</p>
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 0.25rem; margin-top: 0.5rem;">
          <span v-for="asset in store.selected.assets" :key="asset.ticker" class="ticker-chip" style="cursor: pointer;" @click="openDetail(asset.ticker)">
            <strong>{{ asset.ticker }}</strong>
            <AppBadge :variant="directionVariant(asset.direction)">{{ asset.direction }}</AppBadge>
          </span>
        </div>
      </div>

      <div style="margin-top: 1.5rem;">
        <AppButton variant="primary" :full="true" @click="follow">FOLLOW THIS IDEA</AppButton>
        <div v-if="message" class="mario-success">{{ message }}</div>
        <div v-if="store.error" class="mario-error">{{ store.error }}</div>
      </div>
    </AppCard>

    <SecurityDetailModal
      :ticker="selectedTicker"
      :visible="!!selectedTicker"
      @close="selectedTicker = ''"
    />
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useOpportunitiesStore } from "../stores/opportunities";
import AppCard from "../components/AppCard.vue";
import AppBadge from "../components/AppBadge.vue";
import AppButton from "../components/AppButton.vue";
import ChickenLoader from "../components/ChickenLoader.vue";
import SecurityDetailModal from "../components/SecurityDetailModal.vue";

const route = useRoute();
const store = useOpportunitiesStore();
const message = ref("");
const selectedTicker = ref("");

onMounted(() => store.loadDetail(String(route.params.id)));

function directionVariant(direction: string): "active" | "sell" | "hold" {
  const d = direction?.toLowerCase();
  if (d === "buy" || d === "long") return "active";
  if (d === "sell" || d === "short") return "sell";
  return "hold";
}

function openDetail(ticker: string) {
  selectedTicker.value = ticker;
  store.loadSecurityDetail(ticker);
}

async function follow() {
  try {
    await store.follow(String(route.params.id));
    message.value = "Thesis followed successfully.";
  } catch (e: any) {
    message.value = e.message;
  }
}
</script>
