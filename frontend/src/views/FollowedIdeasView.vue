<template>
  <section>
    <h2>Followed Ideas Dashboard</h2>
    <div v-for="thesis in store.items" :key="thesis.id" class="card">
      <h3>Event #{{ thesis.event_id }}</h3>
      <p>{{ thesis.thesis_summary }}</p>
      <p>Follow date: {{ thesis.followed_at }}</p>
      <p>Status: <span class="badge">{{ thesis.latest_state }}</span></p>
      <p>Last update: {{ thesis.latest_explanation }}</p>
      <p>Closed: {{ thesis.closed ? "Yes" : "No" }}</p>
    </div>
    <p v-if="store.error">{{ store.error }}</p>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useThesisStore } from "../stores/theses";

const store = useThesisStore();
onMounted(() => store.load());
</script>
