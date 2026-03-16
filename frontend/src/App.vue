<template>
  <div v-if="isAuthenticated" class="layout">
    <header class="header">
      <div class="flex items-center justify-between">
        <h1 class="text-3xl font-semibold">AI Investment Opportunity Daily</h1>
        <button @click="logout">Log out</button>
      </div>
      <nav>
        <RouterLink to="/">Opportunities</RouterLink>
        <RouterLink to="/followed">Followed Ideas</RouterLink>
        <RouterLink to="/notifications">Notifications</RouterLink>
        <RouterLink to="/watchlist">Watchlist</RouterLink>
        <RouterLink to="/broker">Broker</RouterLink>
      </nav>
    </header>
    <main class="content">
      <RouterView />
    </main>
  </div>
  <RouterView v-else />
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "./stores/auth";

const authStore = useAuthStore();
const router = useRouter();

const isAuthenticated = computed(() => Boolean(localStorage.getItem("token")));

onMounted(async () => {
  if (localStorage.getItem("token")) {
    await authStore.fetchMe();
  }
});

async function logout() {
  authStore.logout();
  await router.push("/login");
}
</script>
