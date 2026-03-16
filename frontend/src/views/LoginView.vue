<template>
  <section>
    <h2>Login</h2>
    <div class="card">
      <label>Email<input v-model="email" type="email" /></label>
      <label>Password<input v-model="password" type="password" /></label>
      <button @click="submit">Login</button>
      <p>
        New user?
        <RouterLink :to="{ path: '/register', query: route.query.redirect ? { redirect: route.query.redirect } : {} }">
          Register here
        </RouterLink>
      </p>
      <p>{{ store.error }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const store = useAuthStore();
const route = useRoute();
const router = useRouter();
const email = ref("");
const password = ref("");

async function submit() {
  await store.login(email.value, password.value);
  if (!store.error) {
    const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/";
    await router.push(redirect);
  }
}
</script>
