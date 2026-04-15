<template>
  <nav class="bottom-nav">
    <RouterLink class="bottom-nav__item" to="/market" exact-active-class="router-link-exact-active">
      <span class="bottom-nav__icon">🏪</span>
      <span>Market</span>
    </RouterLink>
    <RouterLink class="bottom-nav__item" to="/followed">
      <span class="bottom-nav__icon">⭐</span>
      <span>Ideas</span>
    </RouterLink>
    <RouterLink class="bottom-nav__item" to="/notifications">
      <span class="bottom-nav__icon">🔔</span>
      <span>Alerts</span>
      <span v-if="unreadCount > 0" class="mario-badge mario-badge--unread bottom-nav__badge">
        {{ unreadCount }}
      </span>
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useNotificationsStore } from "../stores/notifications";

const notifStore = useNotificationsStore();
const unreadCount = computed(() => notifStore.unreadCount);
</script>
