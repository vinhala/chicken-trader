<template>
  <section>
    <h2>Notifications Center</h2>
    <div v-for="n in store.items" :key="n.id" class="card">
      <h3>{{ n.title }}</h3>
      <p>{{ n.body }}</p>
      <p>Suggested action: {{ n.recommended_action }}</p>
      <p>Time: {{ n.created_at }}</p>
    </div>
    <p v-if="store.error">{{ store.error }}</p>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useNotificationsStore } from "../stores/notifications";

const store = useNotificationsStore();
onMounted(() => store.load());
</script>
