import { defineStore } from "pinia";
import { api } from "./api";

export const useNotificationsStore = defineStore("notifications", {
  state: () => ({
    items: [] as any[],
    error: "",
  }),
  actions: {
    async load() {
      this.error = "";
      try { this.items = await api("/notifications"); }
      catch (e: any) { this.error = e.message; }
    },
  },
});
