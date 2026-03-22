<template>
  <section>
    <div class="section-heading">
      <span style="font-size: 1.5rem;">🪙</span>
      <h2>TODAY'S PICKS</h2>
    </div>

    <div v-if="store.error" class="mario-error">{{ store.error }}</div>

    <div v-if="store.loading" class="mario-empty">
      <ChickenLoader />
    </div>

    <div v-else-if="store.items.length === 0 && !store.error" class="mario-empty">
      <p>NO SIGNALS TODAY</p>
      <p style="font-size: 0.45rem;">Check back tomorrow for new opportunities</p>
    </div>

    <div class="mario-grid">
      <AppCard
        v-for="op in store.items"
        :key="op.event_id"
        color="blue"
        :clickable="true"
        @click="$router.push(`/opportunities/${op.event_id}`)"
      >
        <h3>{{ op.headline }}</h3>
        <p style="font-size: 0.85rem; margin-bottom: 1rem;">
          {{ op.summary ? op.summary.slice(0, 120) + (op.summary.length > 120 ? '…' : '') : '' }}
        </p>
        <div style="display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 0.5rem;">
          <AppBadge variant="sector">{{ op.sector }}</AppBadge>
          <AppBadge variant="ai">AI {{ op.confidence }}</AppBadge>
          <AppBadge :variant="op.expected_market_impact === 'High' ? 'impact-high' : op.expected_market_impact === 'Low' ? 'impact-low' : 'impact-medium'">{{ op.expected_market_impact }} IMPACT</AppBadge>
        </div>
        <p style="font-size: 0.7rem; opacity: 0.6; margin-bottom: 1rem;">Generated: {{ new Date(op.created_at).toLocaleString() }}</p>
        <AppButton
          variant="primary"
          size="sm"
          @click.stop="$router.push(`/opportunities/${op.event_id}`)"
        >VIEW REPORT</AppButton>
      </AppCard>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useOpportunitiesStore } from "../stores/opportunities";
import AppCard from "../components/AppCard.vue";
import AppBadge from "../components/AppBadge.vue";
import AppButton from "../components/AppButton.vue";
import ChickenLoader from "../components/ChickenLoader.vue";

const store = useOpportunitiesStore();
onMounted(() => store.loadDaily());
</script>
