<template>
  <section>
    <h2>Daily Opportunities Dashboard</h2>
    <p v-if="store.error">{{ store.error }}</p>
    <div class="grid">
      <article v-for="op in store.items" :key="op.event_id" class="card">
        <h3>{{ op.headline }}</h3>
        <p>{{ op.summary }}</p>
        <p><span class="badge">{{ op.sector }}</span> <span class="badge">AI {{ op.confidence }}</span></p>
        <RouterLink :to="`/opportunities/${op.event_id}`">View report</RouterLink>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useOpportunitiesStore } from "../stores/opportunities";

const store = useOpportunitiesStore();
onMounted(() => store.loadDaily());
</script>
