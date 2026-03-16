import { defineStore } from "pinia";
import { api } from "./api";

export const useOpportunitiesStore = defineStore("opportunities", {
  state: () => ({
    items: [] as any[],
    selected: null as any,
    error: "",
  }),
  actions: {
    async loadDaily() {
      this.error = "";
      try { this.items = await api("/opportunities"); }
      catch (e: any) { this.error = e.message; }
    },
    async loadDetail(id: string) {
      this.error = "";
      try { this.selected = await api(`/opportunities/${id}`); }
      catch (e: any) { this.error = e.message; }
    },
    async follow(id: string) {
      await api(`/opportunities/${id}/follow`, { method: "POST", body: JSON.stringify({ time_horizon: "event-driven" }) });
    },
  },
});
