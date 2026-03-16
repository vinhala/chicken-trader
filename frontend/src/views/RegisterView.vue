<template>
  <section>
    <h2>Register</h2>
    <div class="card">
      <label>Email<input v-model="email" type="email" /></label>
      <label>Password<input v-model="password" type="password" /></label>
      <label>
        <input v-model="accepted" type="checkbox" />
        I accept the disclaimer and limitation of liability.
      </label>
      <p class="card">
        The app provides AI-generated informational content only, not investment advice. You are solely responsible
        for your decisions. Information is as-is with no warranty; operator is not liable for trading losses.
      </p>
      <button @click="submit">Register</button>
      <p>{{ store.error || message }}</p>
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
const accepted = ref(false);
const message = ref("");

async function submit() {
  await store.register(email.value, password.value, accepted.value);
  if (!store.error) {
    message.value = "Registration successful.";
    const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/";
    await router.push(redirect);
  }
}
</script>
