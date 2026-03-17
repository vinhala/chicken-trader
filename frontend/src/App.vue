<template>
  <div v-if="isAuthenticated" class="layout">
    <header class="mario-header">
      <div style="display:flex;align-items:center;gap:0.6rem;">
        <ChickenLogo :size="36" />
        <h1>CHICKEN TRADER</h1>
      </div>
      <AppButton variant="secondary" size="sm" @click="logout">EXIT</AppButton>
    </header>
    <main class="content">
      <RouterView />
    </main>
    <BottomNav />
  </div>
  <RouterView v-else />
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "./stores/auth";
import AppButton from "./components/AppButton.vue";
import BottomNav from "./components/BottomNav.vue";
import ChickenLogo from "./components/ChickenLogo.vue";

const authStore = useAuthStore();
const router = useRouter();

const isAuthenticated = computed(() => Boolean(authStore.user));

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
