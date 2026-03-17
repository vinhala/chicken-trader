import { defineStore } from "pinia";
import { api } from "./api";

export const useOpportunitiesStore = defineStore("opportunities", {
  state: () => ({
    items: [] as any[],
    selected: null as any,
    error: "",
    loading: false,
    securityDetail: null as any,
    securityDetailLoading: false,
    securityDetailError: "",
  }),
  actions: {
    async loadDaily() {
      this.error = "";
      this.loading = true;
      try { this.items = await api("/opportunities"); }
      catch (e: any) { this.error = e.message; }
      finally { this.loading = false; }
    },
    async loadDetail(id: string) {
      this.error = "";
      this.loading = true;
      this.selected = null;
      try { this.selected = await api(`/opportunities/${id}`); }
      catch (e: any) { this.error = e.message; }
      finally { this.loading = false; }
    },
    async follow(id: string) {
      await api(`/opportunities/${id}/follow`, { method: "POST", body: JSON.stringify({ time_horizon: "event-driven" }) });
    },
    async loadSecurityDetail(ticker: string) {
      this.securityDetailError = "";
      this.securityDetailLoading = true;
      this.securityDetail = null;
      try { this.securityDetail = await api(`/securities/${encodeURIComponent(ticker)}`); }
      catch (e: any) { this.securityDetailError = e.message; }
      finally { this.securityDetailLoading = false; }
    },
  },
});
