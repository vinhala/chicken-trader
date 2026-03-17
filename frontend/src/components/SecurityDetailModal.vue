<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-backdrop" @click.self="$emit('close')">
      <div class="modal-container">
        <AppCard>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <h3 style="margin: 0;">{{ ticker }}</h3>
            <button class="modal-close-btn" @click="$emit('close')">✕</button>
          </div>

          <div v-if="store.securityDetailLoading" style="text-align: center; padding: 1rem;">
            <ChickenLoader label="LOADING..." />
          </div>

          <div v-else-if="store.securityDetailError" class="mario-error">
            {{ store.securityDetailError }}
          </div>

          <div v-else-if="store.securityDetail" class="security-detail-body">
            <div class="security-detail-row">
              <span class="security-detail-label">Name</span>
              <span>{{ store.securityDetail.name || "—" }}</span>
            </div>
            <div class="security-detail-row">
              <span class="security-detail-label">Type</span>
              <AppBadge variant="sector">{{ store.securityDetail.type || "—" }}</AppBadge>
            </div>
            <div class="security-detail-row">
              <span class="security-detail-label">Exchanges</span>
              <span>{{ store.securityDetail.exchanges?.join(", ") || "—" }}</span>
            </div>
            <div class="security-detail-row">
              <span class="security-detail-label">Prev. Close</span>
              <span>
                <template v-if="store.securityDetail.previous_close != null">
                  {{ store.securityDetail.previous_close }}
                  <span v-if="store.securityDetail.previous_close_date" style="opacity: 0.6; font-size: 0.8rem;">
                    ({{ store.securityDetail.previous_close_date }})
                  </span>
                </template>
                <template v-else>—</template>
              </span>
            </div>
          </div>

          <div v-else class="mario-error">
            Security data is currently unavailable.
          </div>
        </AppCard>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import AppCard from "./AppCard.vue";
import AppBadge from "./AppBadge.vue";
import ChickenLoader from "./ChickenLoader.vue";
import { useOpportunitiesStore } from "../stores/opportunities";

const props = defineProps<{ ticker: string; visible: boolean }>();
defineEmits<{ (e: "close"): void }>();

const store = useOpportunitiesStore();
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  width: 100%;
  max-width: 420px;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  color: inherit;
}

.security-detail-body {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.security-detail-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.security-detail-label {
  font-weight: bold;
  min-width: 90px;
  opacity: 0.7;
  font-size: 0.8rem;
  text-transform: uppercase;
}
</style>
